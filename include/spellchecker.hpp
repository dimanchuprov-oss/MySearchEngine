#ifndef MYSEARCHENGINE_SPELLCHECKER_HPP
#define MYSEARCHENGINE_SPELLCHECKER_HPP

#include <cstddef>
#include <string>
#include <vector>

namespace mysearchengine {

class SpellChecker {
public:
    explicit SpellChecker(std::size_t maxDistance = 2) noexcept;

    // Returns the exact OSA Damerau–Levenshtein distance between two terms.
    // The implementation uses linear memory in the length of the shorter term.
    static std::size_t damerauLevenshtein(const std::wstring& first,
                                          const std::wstring& second);

    // Returns the closest vocabulary term within maxDistance_, or an empty
    // string when no suitable correction exists. Ties are resolved
    // lexicographically to keep search results deterministic.
    std::wstring suggest(const std::wstring& term,
                         const std::vector<std::wstring>& vocabulary) const;

    std::size_t maxDistance() const noexcept;

private:
    std::size_t maxDistance_;
};

}  // namespace mysearchengine

#endif
