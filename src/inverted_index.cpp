#include "inverted_index.hpp"

#include "text_processor.hpp"

#include <algorithm>
#include <utility>

namespace mysearchengine {

void PostingList::addOccurrence(std::size_t docId, std::size_t sentenceIndex) {
    Posting* posting = nullptr;
    if (!postings_.empty() && postings_.back().docId == docId) {
        posting = &postings_.back();
    } else if (postings_.empty() || postings_.back().docId < docId) {
        postings_.push_back(Posting{docId, 0, {}});
        posting = &postings_.back();
    } else {
        const auto iterator = std::lower_bound(
            postings_.begin(), postings_.end(), docId,
            [](const Posting& value, std::size_t id) { return value.docId < id; });
        if (iterator == postings_.end() || iterator->docId != docId) {
            posting = &*postings_.insert(iterator, Posting{docId, 0, {}});
        } else {
            posting = &*iterator;
        }
    }

    ++posting->termFrequency;
    if (posting->sentenceIndices.empty() || posting->sentenceIndices.back() != sentenceIndex) {
        posting->sentenceIndices.push_back(sentenceIndex);
    }
}

void PostingList::removeDocument(std::size_t docId) {
    const auto iterator = std::lower_bound(
        postings_.begin(), postings_.end(), docId,
        [](const Posting& value, std::size_t id) { return value.docId < id; });
    if (iterator != postings_.end() && iterator->docId == docId) {
        postings_.erase(iterator);
    }
}

const std::vector<Posting>& PostingList::getPostings() const noexcept {
    return postings_;
}

std::size_t PostingList::getTermFrequency(std::size_t docId) const noexcept {
    const auto iterator = std::lower_bound(
        postings_.begin(), postings_.end(), docId,
        [](const Posting& value, std::size_t id) { return value.docId < id; });
    return iterator != postings_.end() && iterator->docId == docId ? iterator->termFrequency : 0;
}

std::size_t PostingList::getDocumentCount() const noexcept {
    return postings_.size();
}

bool PostingList::empty() const noexcept {
    return postings_.empty();
}

std::size_t PostingList::size() const noexcept {
    return postings_.size();
}

std::vector<Posting>::const_iterator PostingList::begin() const noexcept {
    return postings_.begin();
}

std::vector<Posting>::const_iterator PostingList::end() const noexcept {
    return postings_.end();
}

void InvertedIndex::clear() noexcept {
    table_.clear();
    vocabulary_.clear();
}

void InvertedIndex::build(const DocumentStore& documentStore) {
    std::unordered_map<std::wstring, PostingList> replacementTable;
    std::vector<std::wstring> replacementVocabulary;

    for (const auto& document : documentStore.documents()) {
        for (std::size_t sentenceIndex = 0;
             sentenceIndex < document.sentences.size(); ++sentenceIndex) {
            const auto tokens = TextProcessor::tokenize(document.sentences[sentenceIndex]);
            for (const auto& token : tokens) {
                auto& postings = replacementTable[token];
                postings.addOccurrence(document.docId, sentenceIndex);
            }
        }
    }

    replacementVocabulary.reserve(replacementTable.size());
    for (const auto& entry : replacementTable) {
        replacementVocabulary.push_back(entry.first);
    }
    std::sort(replacementVocabulary.begin(), replacementVocabulary.end());

    table_.swap(replacementTable);
    vocabulary_.swap(replacementVocabulary);
}

void InvertedIndex::addTerm(const std::wstring& term,
                            std::size_t docId,
                            std::size_t sentenceIndex) {
    auto tableEntry = table_.find(term);
    if (tableEntry == table_.end()) {
        tableEntry = table_.emplace(term, PostingList{}).first;
        const auto vocabularyPosition = std::lower_bound(vocabulary_.begin(), vocabulary_.end(), term);
        vocabulary_.insert(vocabularyPosition, term);
    }
    tableEntry->second.addOccurrence(docId, sentenceIndex);
}

void InvertedIndex::removeDocumentTerms(std::size_t docId) {
    for (auto tableIterator = table_.begin(); tableIterator != table_.end();) {
        tableIterator->second.removeDocument(docId);
        if (tableIterator->second.empty()) {
            tableIterator = table_.erase(tableIterator);
            continue;
        }
        ++tableIterator;
    }

    vocabulary_.clear();
    vocabulary_.reserve(table_.size());
    for (const auto& entry : table_) {
        vocabulary_.push_back(entry.first);
    }
    std::sort(vocabulary_.begin(), vocabulary_.end());
}

const PostingList* InvertedIndex::lookup(const std::wstring& term) const noexcept {
    const auto iterator = table_.find(term);
    return iterator == table_.end() ? nullptr : &iterator->second;
}

bool InvertedIndex::contains(const std::wstring& term) const noexcept {
    return table_.find(term) != table_.end();
}

const std::vector<std::wstring>& InvertedIndex::getVocabulary() const noexcept {
    return vocabulary_;
}

const std::vector<std::wstring>& InvertedIndex::vocabulary() const noexcept {
    return vocabulary_;
}

}  // namespace mysearchengine
