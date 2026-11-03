#include "document_store.hpp"

#include "text_processor.hpp"

#include <algorithm>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <system_error>
#include <utility>

namespace mysearchengine {
namespace {

std::string pathForError(const std::filesystem::path& path) {
    return path.string();
}

std::string readFile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Cannot open file: " + pathForError(path));
    }

    std::string contents{std::istreambuf_iterator<char>(input),
                         std::istreambuf_iterator<char>()};
    if (input.bad()) {
        throw std::runtime_error("Cannot read file: " + pathForError(path));
    }
    return contents;
}

}  // namespace

IndexReport DocumentStore::rescan(const std::filesystem::path& directory) {
    std::error_code error;
    const auto root = std::filesystem::canonical(directory, error);
    if (error) {
        throw std::filesystem::filesystem_error("Cannot access directory", directory, error);
    }
    if (!std::filesystem::is_directory(root, error) || error) {
        if (error) {
            throw std::filesystem::filesystem_error("Cannot inspect directory", root, error);
        }
        throw std::invalid_argument("Path is not a directory: " + pathForError(root));
    }

    std::vector<std::filesystem::path> paths;
    std::filesystem::recursive_directory_iterator current(root, error);
    const std::filesystem::recursive_directory_iterator end;
    if (error) {
        throw std::filesystem::filesystem_error("Cannot scan directory", root, error);
    }
    while (current != end) {
        const auto entryPath = current->path();
        const bool regularFile = current->is_regular_file(error);
        if (error) {
            throw std::filesystem::filesystem_error("Cannot inspect file", entryPath, error);
        }
        if (regularFile && entryPath.extension() == ".txt") {
            paths.push_back(entryPath);
        }
        current.increment(error);
        if (error) {
            throw std::filesystem::filesystem_error("Cannot continue directory scan", root, error);
        }
    }
    std::sort(paths.begin(), paths.end());

    std::vector<DocumentMetadata> replacement;
    replacement.reserve(paths.size());
    IndexReport report;
    for (const auto& path : paths) {
        std::wstring decoded;
        try {
            decoded = TextProcessor::decodeUtf8(readFile(path));
        } catch (const std::exception& exception) {
            throw std::runtime_error(pathForError(path) + ": " + exception.what());
        }

        DocumentMetadata document;
        document.docId = replacement.size();
        document.filePath = path;
        document.sentences = TextProcessor::splitSentences(decoded);
        document.wordCount = TextProcessor::countWords(decoded);
        report.sentenceCount += document.sentences.size();
        report.wordCount += document.wordCount;
        replacement.push_back(std::move(document));
    }

    report.documentCount = replacement.size();
    documents_.swap(replacement);
    return report;
}

const std::vector<DocumentMetadata>& DocumentStore::documents() const noexcept {
    return documents_;
}

const DocumentMetadata& DocumentStore::getDocument(std::size_t docId) const {
    if (docId >= documents_.size()) {
        throw std::out_of_range("Document id does not exist");
    }
    return documents_[docId];
}

std::size_t DocumentStore::getTotalDocs() const noexcept {
    return documents_.size();
}

}  // namespace mysearchengine
