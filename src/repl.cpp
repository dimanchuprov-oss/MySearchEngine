#include "repl.hpp"

#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>

namespace mysearchengine {
namespace {

std::string trim(const std::string& text) {
    const auto first = text.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) {
        return {};
    }
    const auto last = text.find_last_not_of(" \t\r\n");
    return text.substr(first, last - first + 1);
}

std::string parsePathArgument(const std::string& argument) {
    const auto value = trim(argument);
    if (value.empty()) {
        throw std::invalid_argument("Usage: setdir <path>");
    }
    if (value.front() != '"') {
        return value;
    }

    std::istringstream parser(value);
    std::string path;
    parser >> std::quoted(path);
    parser >> std::ws;
    if (!parser || !parser.eof() || path.empty()) {
        throw std::invalid_argument("Invalid quoted path. Usage: setdir \"<path>\"");
    }
    return path;
}

}  // namespace

REPL::REPL(DocumentStore& documentStore, std::istream& input, std::ostream& output)
    : documentStore_(documentStore), input_(input), output_(output) {}

void REPL::run() {
    output_ << "MySearchEngine. Enter 'help' for commands.\n";
    std::string line;
    while (output_ << "> " && std::getline(input_, line)) {
        const auto command = trim(line);
        if (command.empty()) {
            continue;
        }
        if (command == ":q" || command == "exit") {
            break;
        }
        processCommand(command);
    }
}

void REPL::processCommand(const std::string& command) {
    if (command == "help") {
        printHelp();
        return;
    }
    if (command == "rescan") {
        if (directory_.empty()) {
            output_ << "Set a directory first with: setdir <path>\n";
            return;
        }
        try {
            const auto report = documentStore_.rescan(directory_);
            output_ << "Index rebuilt: " << report.documentCount << " documents, "
                    << report.sentenceCount << " sentences, " << report.wordCount << " words.\n";
        } catch (const std::exception& exception) {
            output_ << "Rescan failed: " << exception.what() << '\n';
        }
        return;
    }
    if (command.compare(0, 7, "setdir ") == 0 || command == "setdir") {
        try {
            const auto path = std::filesystem::path(parsePathArgument(command.substr(6)));
            std::error_code error;
            if (!std::filesystem::is_directory(path, error)) {
                if (error) {
                    throw std::filesystem::filesystem_error("Cannot inspect directory", path, error);
                }
                throw std::invalid_argument("Path is not a directory: " + path.string());
            }
            directory_ = std::filesystem::canonical(path);
            output_ << "Directory set to: " << directory_.string() << '\n';
        } catch (const std::exception& exception) {
            output_ << "Cannot set directory: " << exception.what() << '\n';
        }
        return;
    }
    output_ << "Search is not implemented yet; use 'help' to see available commands.\n";
}

void REPL::printHelp() {
    output_ << "Commands:\n"
            << "  setdir <path>   Set the directory to scan (quote paths containing spaces)\n"
            << "  rescan          Rebuild the document store from all .txt files\n"
            << "  help            Show this help\n"
            << "  :q, exit        Quit\n"
            << "Search is not implemented yet.\n";
}

}  // namespace mysearchengine
