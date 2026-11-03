#include "document_store.hpp"
#include "repl.hpp"

#include <exception>
#include <iostream>

int main() {
    try {
        mysearchengine::DocumentStore documentStore;
        mysearchengine::REPL repl(documentStore, std::cin, std::cout);
        repl.run();
    } catch (const std::exception& exception) {
        std::cerr << "Fatal error: " << exception.what() << '\n';
        return 1;
    }

    return 0;
}
