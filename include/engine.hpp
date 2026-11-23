#ifndef MYSEARCHENGINE_ENGINE_HPP
#define MYSEARCHENGINE_ENGINE_HPP

#include "document_store.hpp"
#include "inverted_index.hpp"
#include "spellchecker.hpp"

#include <cstddef>
#include <filesystem>
#include <string>
#include <vector>

namespace mysearchengine {

struct SearchResult {
    std::size_t docId = 0;
    std::string filePath;
    std::size_t score = 0;
    std::vector<std::string> snippets;
    bool wasCorrected = false;
    std::string correctedTerm;
};

struct SearchResponse {
    std::vector<SearchResult> results;
    bool wasCorrected = false;
    std::string correctedQuery;
};

class SearchEngine {
public:
    SearchEngine();
    explicit SearchEngine(DocumentStore& documentStore);

    IndexReport rescan(const std::filesystem::path& directory);

    std::vector<SearchResult> search(const std::string& query,
                                     std::size_t maxResults = 10) const;
    SearchResponse searchDetailed(const std::string& query,
                                  std::size_t maxResults = 10) const;

    const InvertedIndex& index() const noexcept;
    const DocumentStore& documentStore() const noexcept;

private:
    DocumentStore ownedDocumentStore_;
    DocumentStore* documentStore_;
    InvertedIndex index_;
    SpellChecker spellChecker_;
};

}  // namespace mysearchengine

#endif
