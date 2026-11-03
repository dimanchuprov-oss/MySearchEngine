#ifndef MYSEARCHENGINE_TEXT_PROCESSOR_HPP
#define MYSEARCHENGINE_TEXT_PROCESSOR_HPP

#include <cstddef>
#include <string>
#include <vector>

namespace mysearchengine {

class TextProcessor {
public:
    static std::wstring decodeUtf8(const std::string& text);
    static std::string encodeUtf8(const std::wstring& text);
    static std::vector<std::wstring> splitSentences(const std::wstring& text);
    static std::vector<std::wstring> tokenize(const std::wstring& text);
    static std::wstring normalize(const std::wstring& text);
    static std::size_t countWords(const std::wstring& text);
};

}  // namespace mysearchengine

#endif
