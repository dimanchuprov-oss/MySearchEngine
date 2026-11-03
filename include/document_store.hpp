#ifndef MYSEARCHENGINE_DOCUMENT_STORE_HPP
#define MYSEARCHENGINE_DOCUMENT_STORE_HPP

#include <cstddef>
#include <filesystem>
#include <string>
#include <vector>

namespace mysearchengine {

struct DocumentMetadata {
    std::size_t docId = 0;
    std::filesystem::path filePath;
    std::vector<std::wstring> sentences;
    std::size_t wordCount = 0;
};

struct IndexReport {
    std::size_t documentCount = 0;
    std::size_t sentenceCount = 0;
    std::size_t wordCount = 0;
};

class DocumentStore {
public:
    IndexReport rescan(const std::filesystem::path& directory);
    const std::vector<DocumentMetadata>& documents() const noexcept;
    const DocumentMetadata& getDocument(std::size_t docId) const;
    std::size_t getTotalDocs() const noexcept;

private:
    std::vector<DocumentMetadata> documents_;
};

}  // namespace mysearchengine

#endif
