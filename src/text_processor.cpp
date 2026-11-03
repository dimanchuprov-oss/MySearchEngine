#include "text_processor.hpp"

#include <cstdint>
#include <stdexcept>
#include <utility>

namespace mysearchengine {
namespace {

std::uint32_t codePointAt(const std::wstring& text, std::size_t& position) {
    const std::uint32_t first = static_cast<std::uint32_t>(text[position++]);
    if constexpr (sizeof(wchar_t) == 2) {
        if (first >= 0xD800 && first <= 0xDBFF) {
            if (position >= text.size()) {
                throw std::invalid_argument("Invalid UTF-16 surrogate pair");
            }
            const std::uint32_t second = static_cast<std::uint32_t>(text[position++]);
            if (second < 0xDC00 || second > 0xDFFF) {
                throw std::invalid_argument("Invalid UTF-16 surrogate pair");
            }
            return 0x10000 + ((first - 0xD800) << 10) + (second - 0xDC00);
        }
        if (first >= 0xDC00 && first <= 0xDFFF) {
            throw std::invalid_argument("Unpaired UTF-16 low surrogate");
        }
    }
    if (first > 0x10FFFF || (first >= 0xD800 && first <= 0xDFFF)) {
        throw std::invalid_argument("Invalid Unicode code point");
    }
    return first;
}

void appendCodePoint(std::wstring& text, std::uint32_t codePoint) {
    if (codePoint > 0x10FFFF || (codePoint >= 0xD800 && codePoint <= 0xDFFF)) {
        throw std::invalid_argument("Invalid Unicode code point");
    }
    if constexpr (sizeof(wchar_t) == 2) {
        if (codePoint > 0xFFFF) {
            codePoint -= 0x10000;
            text.push_back(static_cast<wchar_t>(0xD800 + (codePoint >> 10)));
            text.push_back(static_cast<wchar_t>(0xDC00 + (codePoint & 0x3FF)));
            return;
        }
    }
    text.push_back(static_cast<wchar_t>(codePoint));
}

bool isLetterOrDigit(std::uint32_t codePoint) {
    return (codePoint >= '0' && codePoint <= '9') ||
           (codePoint >= 'A' && codePoint <= 'Z') ||
           (codePoint >= 'a' && codePoint <= 'z') ||
           (codePoint >= 0x00C0 && codePoint <= 0x02AF &&
            codePoint != 0x00D7 && codePoint != 0x00F7) ||
           (codePoint >= 0x0400 && codePoint <= 0x052F);
}

bool isWhitespace(std::uint32_t codePoint) {
    return codePoint == 0x20 || (codePoint >= 0x09 && codePoint <= 0x0D) ||
           codePoint == 0x85 || codePoint == 0xA0 || codePoint == 0x1680 ||
           (codePoint >= 0x2000 && codePoint <= 0x200A) ||
           codePoint == 0x2028 || codePoint == 0x2029 ||
           codePoint == 0x202F || codePoint == 0x205F || codePoint == 0x3000;
}

std::uint32_t lowercase(std::uint32_t codePoint) {
    if (codePoint >= 'A' && codePoint <= 'Z') {
        return codePoint + ('a' - 'A');
    }
    if (codePoint >= 0x0410 && codePoint <= 0x042F) {
        return codePoint + 0x20;
    }
    if (codePoint >= 0x0400 && codePoint <= 0x040F) {
        return codePoint + 0x50;
    }
    return codePoint;
}

std::wstring trim(const std::wstring& text) {
    std::size_t start = 0;
    while (start < text.size()) {
        std::size_t position = start;
        const auto codePoint = codePointAt(text, position);
        if (!isWhitespace(codePoint)) {
            break;
        }
        start = position;
    }

    std::size_t end = text.size();
    while (end > start) {
        std::size_t position = end - 1;
        if constexpr (sizeof(wchar_t) == 2) {
            const auto last = static_cast<std::uint32_t>(text[position]);
            if (last >= 0xDC00 && last <= 0xDFFF && position > start) {
                --position;
            }
        }
        std::size_t next = position;
        const auto codePoint = codePointAt(text, next);
        if (!isWhitespace(codePoint)) {
            break;
        }
        end = position;
    }
    return text.substr(start, end - start);
}

}  // namespace

std::wstring TextProcessor::decodeUtf8(const std::string& text) {
    std::wstring result;
    result.reserve(text.size());

    for (std::size_t i = 0; i < text.size();) {
        const auto first = static_cast<unsigned char>(text[i++]);
        std::uint32_t codePoint = 0;
        std::size_t continuationCount = 0;

        if (first <= 0x7F) {
            codePoint = first;
        } else if (first >= 0xC2 && first <= 0xDF) {
            codePoint = first & 0x1F;
            continuationCount = 1;
        } else if (first >= 0xE0 && first <= 0xEF) {
            codePoint = first & 0x0F;
            continuationCount = 2;
        } else if (first >= 0xF0 && first <= 0xF4) {
            codePoint = first & 0x07;
            continuationCount = 3;
        } else {
            throw std::invalid_argument("Invalid UTF-8 leading byte");
        }

        if (text.size() - i < continuationCount) {
            throw std::invalid_argument("Truncated UTF-8 sequence");
        }
        for (std::size_t j = 0; j < continuationCount; ++j) {
            const auto next = static_cast<unsigned char>(text[i++]);
            if ((next & 0xC0) != 0x80) {
                throw std::invalid_argument("Invalid UTF-8 continuation byte");
            }
            codePoint = (codePoint << 6) | (next & 0x3F);
        }

        if ((continuationCount == 1 && codePoint < 0x80) ||
            (continuationCount == 2 && codePoint < 0x800) ||
            (continuationCount == 3 && codePoint < 0x10000) ||
            codePoint > 0x10FFFF || (codePoint >= 0xD800 && codePoint <= 0xDFFF)) {
            throw std::invalid_argument("Invalid UTF-8 code point");
        }
        appendCodePoint(result, codePoint);
    }
    return result;
}

std::string TextProcessor::encodeUtf8(const std::wstring& text) {
    std::string result;
    result.reserve(text.size());
    for (std::size_t i = 0; i < text.size();) {
        const auto codePoint = codePointAt(text, i);
        if (codePoint <= 0x7F) {
            result.push_back(static_cast<char>(codePoint));
        } else if (codePoint <= 0x7FF) {
            result.push_back(static_cast<char>(0xC0 | (codePoint >> 6)));
            result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
        } else if (codePoint <= 0xFFFF) {
            result.push_back(static_cast<char>(0xE0 | (codePoint >> 12)));
            result.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3F)));
            result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
        } else {
            result.push_back(static_cast<char>(0xF0 | (codePoint >> 18)));
            result.push_back(static_cast<char>(0x80 | ((codePoint >> 12) & 0x3F)));
            result.push_back(static_cast<char>(0x80 | ((codePoint >> 6) & 0x3F)));
            result.push_back(static_cast<char>(0x80 | (codePoint & 0x3F)));
        }
    }
    return result;
}

std::vector<std::wstring> TextProcessor::splitSentences(const std::wstring& text) {
    std::vector<std::wstring> sentences;
    std::size_t start = 0;
    for (std::size_t i = 0; i < text.size();) {
        const auto characterStart = i;
        const auto codePoint = codePointAt(text, i);
        if (codePoint == '.' || codePoint == '!' || codePoint == '?' ||
            codePoint == '\n' || codePoint == '\r') {
            const auto end = codePoint == '\n' || codePoint == '\r' ? characterStart : i;
            auto sentence = trim(text.substr(start, end - start));
            if (!sentence.empty()) {
                sentences.push_back(std::move(sentence));
            }
            start = i;
        }
    }
    auto sentence = trim(text.substr(start));
    if (!sentence.empty()) {
        sentences.push_back(std::move(sentence));
    }
    return sentences;
}

std::vector<std::wstring> TextProcessor::tokenize(const std::wstring& text) {
    std::vector<std::wstring> tokens;
    std::size_t start = std::wstring::npos;
    for (std::size_t i = 0; i < text.size();) {
        const auto characterStart = i;
        const auto codePoint = codePointAt(text, i);
        if (isLetterOrDigit(codePoint)) {
            if (start == std::wstring::npos) {
                start = characterStart;
            }
        } else if (start != std::wstring::npos) {
            tokens.push_back(normalize(text.substr(start, characterStart - start)));
            start = std::wstring::npos;
        }
    }
    if (start != std::wstring::npos) {
        tokens.push_back(normalize(text.substr(start)));
    }
    return tokens;
}

std::wstring TextProcessor::normalize(const std::wstring& text) {
    std::wstring result;
    result.reserve(text.size());
    for (std::size_t i = 0; i < text.size();) {
        appendCodePoint(result, lowercase(codePointAt(text, i)));
    }
    return result;
}

std::size_t TextProcessor::countWords(const std::wstring& text) {
    return tokenize(text).size();
}

}  // namespace mysearchengine
