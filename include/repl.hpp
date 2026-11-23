#ifndef MYSEARCHENGINE_REPL_HPP
#define MYSEARCHENGINE_REPL_HPP

#include "engine.hpp"

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

    SearchEngine engine_;
    std::istream& input_;
    std::ostream& output_;
    std::filesystem::path directory_;
};

}  // namespace mysearchengine

#endif
