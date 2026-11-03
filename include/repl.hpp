#ifndef MYSEARCHENGINE_REPL_HPP
#define MYSEARCHENGINE_REPL_HPP

#include "document_store.hpp"

#include <filesystem>
#include <iosfwd>
#include <string>

namespace mysearchengine {

class REPL {
public:
    REPL(DocumentStore& documentStore, std::istream& input, std::ostream& output);
    void run();

private:
    void processCommand(const std::string& command);
    void printHelp();

    DocumentStore& documentStore_;
    std::istream& input_;
    std::ostream& output_;
    std::filesystem::path directory_;
};

}  // namespace mysearchengine

#endif
