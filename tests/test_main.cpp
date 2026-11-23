#include "document_store.hpp"
#include "engine.hpp"
#include "inverted_index.hpp"
#include "repl.hpp"
#include "spellchecker.hpp"
#include "text_processor.hpp"

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

namespace {

void require(bool condition, const std::string& message) {
    if (!condition) {
        throw std::runtime_error(message);
    }
}

class TemporaryDirectory {
public:
    TemporaryDirectory() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        path_ = std::filesystem::temp_directory_path() /
                ("mysearchengine test-" + std::to_string(stamp));
        std::filesystem::create_directories(path_);
    }

    ~TemporaryDirectory() {
        std::error_code error;
        std::filesystem::remove_all(path_, error);
    }

    const std::filesystem::path& path() const noexcept {
        return path_;
    }

private:
    std::filesystem::path path_;
};

void writeFile(const std::filesystem::path& path, const std::string& contents) {
    std::filesystem::create_directories(path.parent_path());
    std::ofstream output(path, std::ios::binary);
    if (!output) {
        throw std::runtime_error("Failed to create test file");
    }
    output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
    if (!output) {
        throw std::runtime_error("Failed to write test file");
    }
}

void testUtf8AndTextProcessing() {
    const std::string input = "ПрИвЕт, ЁЖ! Hello.\nМир?";
    const auto decoded = mysearchengine::TextProcessor::decodeUtf8(input);
    require(mysearchengine::TextProcessor::encodeUtf8(decoded) == input,
            "UTF-8 round trip failed");
    const std::string supplementaryCharacter = "\xF0\x9F\x90\x88";
    require(mysearchengine::TextProcessor::encodeUtf8(
                mysearchengine::TextProcessor::decodeUtf8(supplementaryCharacter)) ==
                supplementaryCharacter,
            "Supplementary Unicode character round trip failed");

    const auto tokens = mysearchengine::TextProcessor::tokenize(decoded);
    require(tokens.size() == 4, "Unexpected token count");
    require(tokens[0] == L"привет" && tokens[1] == L"ёж" &&
                tokens[2] == L"hello" && tokens[3] == L"мир",
            "Unicode token normalization failed");
    const auto tokensWithoutDigits = mysearchengine::TextProcessor::tokenize(L"abc 123 дефис-45");
    require(tokensWithoutDigits.size() == 2 && tokensWithoutDigits[0] == L"abc" &&
                tokensWithoutDigits[1] == L"дефис",
            "Digits were not removed from text tokens");

    const auto sentences = mysearchengine::TextProcessor::splitSentences(decoded);
    require(sentences.size() == 3, "Unexpected sentence count");
    require(sentences[0] == L"ПрИвЕт, ЁЖ!", "Sentence text was not preserved");

    bool rejectedInvalidUtf8 = false;
    try {
        (void)mysearchengine::TextProcessor::decodeUtf8("\xC0\xAF");
    } catch (const std::invalid_argument&) {
        rejectedInvalidUtf8 = true;
    }
    require(rejectedInvalidUtf8, "Invalid UTF-8 was accepted");
}

void testDocumentStoreRescan() {
    TemporaryDirectory temporaryDirectory;
    const auto root = temporaryDirectory.path();
    writeFile(root / "nested" / "first.txt", "Первая строка.\nВторая строка!");
    writeFile(root / "second.txt", "HELLO, мир.");
    writeFile(root / "ignored.md", "not indexed");

    mysearchengine::DocumentStore store;
    const auto firstReport = store.rescan(root);
    require(firstReport.documentCount == 2 && store.getTotalDocs() == 2,
            "Initial scan did not include exactly the .txt files");
    require(firstReport.sentenceCount == 3, "Unexpected sentence count in scan report");
    require(firstReport.wordCount == 6, "Unexpected word count in scan report");
    require(store.getDocument(0).filePath.is_absolute(),
            "Stored document path is not absolute");
    require(store.getDocument(0).sentences.size() == 2,
            "Document sentences were not stored");

    std::filesystem::remove(root / "second.txt");
    writeFile(root / "nested" / "first.txt", "Измененный текст.");
    writeFile(root / "third.txt", "Новый документ.");
    const auto secondReport = store.rescan(root);
    require(secondReport.documentCount == 2 && store.getTotalDocs() == 2,
            "Full rescan did not replace deleted and added documents");
    require(secondReport.wordCount == 4, "Full rescan retained stale document content");

    bool rejectedInvalidDirectory = false;
    try {
        (void)store.rescan(root / "missing");
    } catch (const std::filesystem::filesystem_error&) {
        rejectedInvalidDirectory = true;
    }
    require(rejectedInvalidDirectory, "Missing scan directory was accepted");
    require(store.getTotalDocs() == 2, "Failed scan discarded the previous document store");

    writeFile(root / "invalid.txt", "\xF0\x28\x8C\x28");
    bool rejectedInvalidFile = false;
    try {
        (void)store.rescan(root);
    } catch (const std::runtime_error&) {
        rejectedInvalidFile = true;
    }
    require(rejectedInvalidFile, "Invalid UTF-8 document was accepted");
    require(store.getTotalDocs() == 2, "Failed UTF-8 scan partially replaced the document store");
}

void testReplCommands() {
    TemporaryDirectory temporaryDirectory;
    writeFile(temporaryDirectory.path() / "note.txt", "Тестовый документ.");

    std::istringstream input("setdir \"" + temporaryDirectory.path().string() +
                             "\"\nrescan\nhelp\nтестовый\nexit\n");
    std::ostringstream output;
    mysearchengine::DocumentStore store;
    mysearchengine::REPL repl(store, input, output);
    repl.run();

    const auto text = output.str();
    require(text.find("Directory set to:") != std::string::npos,
            "REPL did not accept setdir");
    require(text.find("1 documents") != std::string::npos,
            "REPL did not report the rescan");
    require(text.find("Search indexed documents") != std::string::npos,
            "REPL help does not identify the search command");
    require(text.find("note.txt") != std::string::npos &&
                text.find("Тестовый документ.") != std::string::npos,
            "REPL did not display a search result and snippet");
    require(store.getTotalDocs() == 1, "REPL rescan did not populate the document store");
}

void testSearchEngine() {
    TemporaryDirectory temporaryDirectory;
    const auto root = temporaryDirectory.path();
    writeFile(root / "high.txt", "Alpha alpha beta. Extra context.");
    writeFile(root / "low.txt", "Alpha beta.");
    writeFile(root / "other.txt", "Alpha only.");

    mysearchengine::DocumentStore store;
    mysearchengine::SearchEngine engine(store);
    const auto report = engine.rescan(root);
    require(report.documentCount == 3, "Search engine did not index all documents");

    const auto exact = engine.search("alpha beta", 10);
    require(exact.size() == 2, "AND search returned an unexpected number of documents");
    require(exact[0].filePath.find("high.txt") != std::string::npos && exact[0].score == 3,
            "Search results were not ranked by term frequency");
    require(exact[0].snippets.size() == 1 &&
                exact[0].snippets[0].find("Alpha alpha beta") != std::string::npos,
            "Search result did not include the matching snippet");

    const auto corrected = engine.searchDetailed("alhpa beta", 10);
    require(corrected.wasCorrected && corrected.correctedQuery == "alpha beta",
            "Typo correction did not produce the expected query");
    require(corrected.results.size() == 2 && corrected.results[0].wasCorrected,
            "Corrected search did not return ranked results");

    require(mysearchengine::SpellChecker::damerauLevenshtein(L"alhpa", L"alpha") == 1,
            "Damerau-Levenshtein transposition distance is incorrect");
    require(engine.search("missing").empty(), "Unknown terms should return no results");
}

void testPostingListAndRescan() {
    mysearchengine::PostingList postings;
    postings.addOccurrence(2, 1);
    postings.addOccurrence(2, 1);
    postings.addOccurrence(2, 3);
    postings.addOccurrence(5, 0);
    require(postings.getDocumentCount() == 2 && postings.getTermFrequency(2) == 3,
            "PostingList did not aggregate term occurrences");
    require(postings.getPostings()[0].sentenceIndices.size() == 2,
            "PostingList did not deduplicate sentence positions");
    postings.removeDocument(2);
    require(postings.getDocumentCount() == 1 && postings.getTermFrequency(2) == 0,
            "PostingList did not remove a document");

    TemporaryDirectory temporaryDirectory;
    const auto root = temporaryDirectory.path();
    writeFile(root / "old.txt", "obsolete token.");
    mysearchengine::SearchEngine engine;
    engine.rescan(root);
    require(!engine.search("obsolete").empty(), "Initial engine index is missing a term");

    std::filesystem::remove(root / "old.txt");
    writeFile(root / "new.txt", "current token.");
    engine.rescan(root);
    require(engine.search("obsolete").empty(), "Rescan retained a deleted term");
    require(engine.search("current").size() == 1, "Rescan did not index a new document");
}

}  // namespace

int main() {
    try {
        testUtf8AndTextProcessing();
        testDocumentStoreRescan();
        testReplCommands();
        testSearchEngine();
        testPostingListAndRescan();
    } catch (const std::exception& exception) {
        std::cerr << "Test failure: " << exception.what() << '\n';
        return 1;
    }
    std::cout << "All tests passed\n";
    return 0;
}
