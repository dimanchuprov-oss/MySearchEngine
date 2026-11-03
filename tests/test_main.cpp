#include "document_store.hpp"
#include "repl.hpp"
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
                             "\"\nrescan\nhelp\nexit\n");
    std::ostringstream output;
    mysearchengine::DocumentStore store;
    mysearchengine::REPL repl(store, input, output);
    repl.run();

    const auto text = output.str();
    require(text.find("Directory set to:") != std::string::npos,
            "REPL did not accept setdir");
    require(text.find("1 documents") != std::string::npos,
            "REPL did not report the rescan");
    require(text.find("Search is not implemented yet") != std::string::npos,
            "REPL help does not identify the unimplemented search");
    require(store.getTotalDocs() == 1, "REPL rescan did not populate the document store");
}

}  // namespace

int main() {
    try {
        testUtf8AndTextProcessing();
        testDocumentStoreRescan();
        testReplCommands();
    } catch (const std::exception& exception) {
        std::cerr << "Test failure: " << exception.what() << '\n';
        return 1;
    }
    std::cout << "All tests passed\n";
    return 0;
}
