#include "spellchecker.hpp"

#include <algorithm>
#include <utility>

namespace mysearchengine {

SpellChecker::SpellChecker(std::size_t maxDistance) noexcept
    : maxDistance_(maxDistance) {}

std::size_t SpellChecker::damerauLevenshtein(const std::wstring& first,
                                             const std::wstring& second) {
    // Keep the shorter term in the columns so the three working rows use
    // O(min(first.size(), second.size())) memory.
    const std::wstring* rows = &first;
    const std::wstring* columns = &second;
    if (columns->size() > rows->size()) {
        std::swap(rows, columns);
    }

    const auto rowCount = rows->size();
    const auto columnCount = columns->size();
    if (columnCount == 0) {
        return rowCount;
    }

    std::vector<std::size_t> previousPrevious(columnCount + 1, 0);
    std::vector<std::size_t> previous(columnCount + 1, 0);
    std::vector<std::size_t> current(columnCount + 1, 0);
    for (std::size_t column = 0; column <= columnCount; ++column) {
        previous[column] = column;
    }

    for (std::size_t row = 1; row <= rowCount; ++row) {
        current[0] = row;
        for (std::size_t column = 1; column <= columnCount; ++column) {
            const auto substitutionCost = (*rows)[row - 1] == (*columns)[column - 1] ? 0 : 1;
            current[column] = std::min({
                previous[column] + 1,
                current[column - 1] + 1,
                previous[column - 1] + substitutionCost,
            });

            if (row > 1 && column > 1 &&
                (*rows)[row - 1] == (*columns)[column - 2] &&
                (*rows)[row - 2] == (*columns)[column - 1]) {
                current[column] = std::min(current[column],
                                            previousPrevious[column - 2] + 1);
            }
        }

        previousPrevious.swap(previous);
        previous.swap(current);
    }

    return previous[columnCount];
}

std::wstring SpellChecker::suggest(const std::wstring& term,
                                   const std::vector<std::wstring>& vocabulary) const {
    std::wstring best;
    auto bestDistance = maxDistance_ + 1;

    for (const auto& candidate : vocabulary) {
        const auto lengthDifference = term.size() > candidate.size()
                                          ? term.size() - candidate.size()
                                          : candidate.size() - term.size();
        if (lengthDifference > maxDistance_) {
            continue;
        }

        const auto distance = damerauLevenshtein(term, candidate);
        if (distance > maxDistance_ ||
            (distance == bestDistance && !best.empty() && candidate >= best)) {
            continue;
        }
        bestDistance = distance;
        best = candidate;
    }

    return best;
}

std::size_t SpellChecker::maxDistance() const noexcept {
    return maxDistance_;
}

}  // namespace mysearchengine
