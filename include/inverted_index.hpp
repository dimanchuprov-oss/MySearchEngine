#ifndef MYSEARCHENGINE_INVERTED_INDEX_HPP
#define MYSEARCHENGINE_INVERTED_INDEX_HPP

#include "document_store.hpp"

#include <cstddef>
#include <string>
#include <unordered_map>
#include <vector>

namespace mysearchengine {

struct Posting {
    std::size_t docId = 0;
    std::size_t termFrequency = 0;
    std::vector<std::size_t> sentenceIndices;
};

class PostingList {
public:
    void addOccurrence(std::size_t docId, std::size_t sentenceIndex);
    void removeDocument(std::size_t docId);

    const std::vector<Posting>& getPostings() const noexcept;
    std::size_t getTermFrequency(std::size_t docId) const noexcept;
    std::size_t getDocumentCount() const noexcept;

    bool empty() const noexcept;
    std::size_t size() const noexcept;
    std::vector<Posting>::const_iterator begin() const noexcept;
    std::vector<Posting>::const_iterator end() const noexcept;

private:
    std::vector<Posting> postings_;
};

class InvertedIndex {
public:
    void clear() noexcept;
    void build(const DocumentStore& documentStore);
    void addTerm(const std::wstring& term, std::size_t docId, std::size_t sentenceIndex);
    void removeDocumentTerms(std::size_t docId);

    const PostingList* lookup(const std::wstring& term) const noexcept;
    bool contains(const std::wstring& term) const noexcept;
    const std::vector<std::wstring>& getVocabulary() const noexcept;
    const std::vector<std::wstring>& vocabulary() const noexcept;

private:
    std::unordered_map<std::wstring, PostingList> table_;
    std::vector<std::wstring> vocabulary_;
};

}  // namespace mysearchengine

#endif
