#include "engine.hpp"

#include "text_processor.hpp"

#include <algorithm>
#include <unordered_map>
#include <unordered_set>
#include <utility>

namespace mysearchengine {
namespace {

struct Match {
    std::size_t score = 0;
    std::vector<std::size_t> sentenceIndices;
};

void appendSentenceIndices(std::vector<std::size_t>& target,
                           const std::vector<std::size_t>& source) {
    target.insert(target.end(), source.begin(), source.end());
}

std::string joinTerms(const std::vector<std::wstring>& terms) {
    std::string result;
    for (std::size_t index = 0; index < terms.size(); ++index) {
        if (index != 0) {
            result.push_back(' ');
        }
        result += TextProcessor::encodeUtf8(terms[index]);
    }
    return result;
}

}  // namespace

SearchEngine::SearchEngine()
    : ownedDocumentStore_(), documentStore_(&ownedDocumentStore_), index_(), spellChecker_() {}

SearchEngine::SearchEngine(DocumentStore& documentStore)
    : ownedDocumentStore_(), documentStore_(&documentStore), index_(), spellChecker_() {}

IndexReport SearchEngine::rescan(const std::filesystem::path& directory) {
    const auto report = documentStore_->rescan(directory);
    InvertedIndex replacement;
    replacement.build(*documentStore_);
    index_ = std::move(replacement);
    return report;
}

std::vector<SearchResult> SearchEngine::search(const std::string& query,
                                               std::size_t maxResults) const {
    return searchDetailed(query, maxResults).results;
}

SearchResponse SearchEngine::searchDetailed(const std::string& query,
                                            std::size_t maxResults) const {
    SearchResponse response;
    const auto decodedQuery = TextProcessor::decodeUtf8(query);
    const auto rawTerms = TextProcessor::tokenize(decodedQuery);

    std::vector<std::wstring> terms;
    std::unordered_set<std::wstring> seenTerms;
    terms.reserve(rawTerms.size());
    for (const auto& term : rawTerms) {
        if (seenTerms.insert(term).second) {
            terms.push_back(term);
        }
    }
    if (terms.empty()) {
        return response;
    }

    bool wasCorrected = false;
    std::vector<std::wstring> correctedTerms;
    std::unordered_set<std::wstring> seenCorrectedTerms;
    correctedTerms.reserve(terms.size());
    for (auto& term : terms) {
        if (index_.lookup(term) != nullptr) {
            // Keep going so the final term list can be deduplicated after
            // corrections as well as before them.
        } else {
            const auto suggestion = spellChecker_.suggest(term, index_.vocabulary());
            if (suggestion.empty()) {
                return response;
            }
            term = suggestion;
            wasCorrected = true;
        }

        if (seenCorrectedTerms.insert(term).second) {
            correctedTerms.push_back(term);
        }
    }
    terms.swap(correctedTerms);
    if (wasCorrected) {
        response.wasCorrected = true;
        response.correctedQuery = joinTerms(terms);
    }

    std::unordered_map<std::size_t, Match> matches;
    bool firstTerm = true;
    for (const auto& term : terms) {
        const auto* postings = index_.lookup(term);
        if (postings == nullptr) {
            return response;
        }

        if (firstTerm) {
            for (const auto& posting : *postings) {
                matches.emplace(posting.docId,
                                Match{posting.termFrequency, posting.sentenceIndices});
            }
            firstTerm = false;
            continue;
        }

        std::unordered_map<std::size_t, Match> intersection;
        intersection.reserve(std::min(matches.size(), postings->size()));
        for (const auto& posting : *postings) {
            const auto previous = matches.find(posting.docId);
            if (previous == matches.end()) {
                continue;
            }

            Match match = previous->second;
            match.score += posting.termFrequency;
            appendSentenceIndices(match.sentenceIndices, posting.sentenceIndices);
            intersection.emplace(posting.docId, std::move(match));
        }
        matches.swap(intersection);
        if (matches.empty()) {
            return response;
        }
    }

    std::vector<std::pair<std::size_t, Match>> ranked;
    ranked.reserve(matches.size());
    for (auto& entry : matches) {
        ranked.emplace_back(entry.first, std::move(entry.second));
    }
    std::sort(ranked.begin(), ranked.end(), [&](const auto& left, const auto& right) {
        if (left.second.score != right.second.score) {
            return left.second.score > right.second.score;
        }
        const auto& leftPath = documentStore_->getDocument(left.first).filePath;
        const auto& rightPath = documentStore_->getDocument(right.first).filePath;
        if (leftPath != rightPath) {
            return leftPath.string() < rightPath.string();
        }
        return left.first < right.first;
    });

    const auto resultCount = std::min(maxResults, ranked.size());
    response.results.reserve(resultCount);
    for (std::size_t rank = 0; rank < resultCount; ++rank) {
        const auto docId = ranked[rank].first;
        const auto& match = ranked[rank].second;
        const auto& document = documentStore_->getDocument(docId);

        auto sentenceIndices = match.sentenceIndices;
        std::sort(sentenceIndices.begin(), sentenceIndices.end());
        sentenceIndices.erase(std::unique(sentenceIndices.begin(), sentenceIndices.end()),
                              sentenceIndices.end());

        SearchResult result;
        result.docId = docId;
        result.filePath = document.filePath.string();
        result.score = match.score;
        result.wasCorrected = response.wasCorrected;
        if (response.wasCorrected) {
            result.correctedTerm = response.correctedQuery;
        }
        for (const auto sentenceIndex : sentenceIndices) {
            if (result.snippets.size() == 3) {
                break;
            }
            if (sentenceIndex < document.sentences.size()) {
                result.snippets.push_back(TextProcessor::encodeUtf8(
                    document.sentences[sentenceIndex]));
            }
        }
        response.results.push_back(std::move(result));
    }

    return response;
}

const InvertedIndex& SearchEngine::index() const noexcept {
    return index_;
}

const DocumentStore& SearchEngine::documentStore() const noexcept {
    return *documentStore_;
}

}  // namespace mysearchengine
