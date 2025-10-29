# Geneweb Business Logic Test Plan

## Overview
This test plan covers the core business logic of the Geneweb OCaml application. It is designed to validate current implementation with business stakeholders and serve as a foundation for creating unit and integration tests in the Python migration.

**Current Test Coverage**: 50 unit tests across 6 functional modules (Sosa, Place, Calendar, Wiki, Merge, Util)

## Test Categories

### Sosa Genealogical Numbering System (6 tests)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| SOSA-001 | Sosa number equality comparison | Valid Sosa numbers | 1. Compare Sosa.zero with Sosa.zero<br>2. Compare Sosa.one with Sosa.one<br>3. Compare Sosa.zero with Sosa.one | 1. Returns true<br>2. Returns true<br>3. Returns false | | | Core equality logic |
| SOSA-002 | Integer to Sosa conversion | Valid integer inputs | 1. Convert 0 to Sosa<br>2. Convert 1 to Sosa | 1. Equals Sosa.zero<br>2. Equals Sosa.one | | | Number system conversion |
| SOSA-003 | String to Sosa conversion and formatting | Valid string/Sosa inputs | 1. Convert "0" to Sosa<br>2. Convert Sosa.zero to string<br>3. Test complex divisions: 1000/1000, 2000/1000, 234000/1000 | 1. Equals Sosa.zero<br>2. Returns "0"<br>3. Returns "1", "2", "234" | | | String representation |
| SOSA-004 | Number formatting with separators | Large Sosa numbers | Format numbers 1, 10, 100, 1000, 10000, 100000, 1000000 with comma separator | Returns "1", "10", "100", "1,000", "10,000", "100,000", "1,000,000" | | | Display formatting |
| SOSA-005 | Generation calculation from Sosa | Sosa numbers 1-15 | Calculate generation for each Sosa number | Returns generations [1,2,2,3,3,3,3,4,4,4,4,4,4,4,4] | | | Genealogical tree levels |
| SOSA-006 | Branch path calculation | Sosa number 38 | Calculate branch path for Sosa 38 | Returns [0,0,1,1,0] | | | Tree navigation path |

### Place and Location Management (5 tests)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| PLACE-001 | Place name normalization | Raw place string with brackets | 1. Normalize "[foo-bar] - boobar (baz)"<br>2. Normalize "[foo-bar - boobar (baz)"<br>3. Normalize "[foo-bar] boobar (baz)" | 1. Returns "foo-bar, boobar (baz)"<br>2. Returns "[foo-bar - boobar (baz)"<br>3. Returns "[foo-bar] boobar (baz)" | | | Standardized place format |
| PLACE-002 | Suburb extraction from place | Place string with suburb notation | 1. Split "[foo-bar] - boobar (baz)"<br>2. Test with em-dash "–"<br>3. Test with en-dash "—"<br>4. Test without suburb "boobar (baz)" | 1-3. Returns ("foo-bar", "boobar (baz)")<br>4. Returns ("", "boobar (baz)") | | | Geographic hierarchy parsing |
| PLACE-003 | Suburb-only extraction | Place with/without suburb | 1. Extract suburb from "[foo-bar] - boobar (baz)"<br>2. Extract from "boobar (baz)" | 1. Returns "foo-bar"<br>2. Returns "" | | | Suburb isolation |
| PLACE-004 | Place without suburb | Place with/without suburb | 1. Remove suburb from "[foo-bar] - boobar (baz)"<br>2. Process "boobar (baz)" | Both return "boobar (baz)" | | | Main location extraction |
| PLACE-005 | Place comparison for sorting | Different place combinations | 1. Compare identical places<br>2. Compare different places<br>3. Compare with/without suburbs<br>4. Compare with unicode characters | Correct alphabetical ordering (-1, 0, 1) | | | Sorting functionality |

### Calendar and Date Systems (7 tests)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| CAL-001 | Gregorian to SDN conversion failure | Incomplete date data | Convert dates with day=0 or month=0 to SDN | Expected to fail due to Calendar library limitation | | | Known limitation - issue #2172 |
| CAL-002 | Julian to SDN conversion failure | Incomplete date data | Convert Julian dates with missing components | Expected to fail due to Calendar library limitation | | | Calendar system constraint |
| CAL-003 | French calendar to SDN conversion failure | French calendar dates | Convert French Revolutionary calendar dates | Expected to fail due to Calendar library limitation | | | Historical calendar support |
| CAL-004 | Hebrew calendar to SDN conversion failure | Hebrew calendar dates | Convert Hebrew calendar dates | Expected to fail due to Calendar library limitation | | | Religious calendar support |
| CAL-005 | Gregorian to Julian round-trip | Valid and incomplete dates | 1. Convert Gregorian to Julian<br>2. Convert back to Gregorian | Original date preserved for both complete and partial dates | | | Calendar system accuracy |
| CAL-006 | Gregorian to French round-trip | Valid date data | 1. Convert Gregorian to French Revolutionary<br>2. Convert back to Gregorian | Original date preserved | | | Historical calendar conversion |
| CAL-007 | Gregorian to Hebrew round-trip | Valid date data | 1. Convert Gregorian to Hebrew<br>2. Convert back to Gregorian | Original date preserved | | | Religious calendar conversion |

### Wiki Markup and Links Processing (16 tests)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| WIKI-001 | Page link parsing | Wiki page link syntax | Parse "[[[aaa/bbb]]]" | Returns WLpage(13, ([], "aaa"), "aaa", "", "bbb") | | | Page reference processing |
| WIKI-002 | Person link parsing | Wiki person link syntax | Parse "[[ccc/ddd]]" | Returns WLperson(11, ("ccc", "ddd", 0), Some "ccc ddd", None) | | | Person reference processing |
| WIKI-003 | Person link with custom text | Person link with display text | Parse "[[ccc/ddd/Texte]]" | Returns WLperson(17, ("ccc", "ddd", 0), Some "Texte", None) | | | Custom display text |
| WIKI-004 | Person link with occurrence number | Person with numeric suffix | Parse "[[ccc/ddd/1/Ccc Ddd]]" | Returns WLperson(21, ("ccc", "ddd", 1), Some "Ccc Ddd", None) | | | Disambiguation handling |
| WIKI-005 | Person link with title and subtitle | Complex person link | Parse "[[ccc/ddd/Texte;Texte 2]]" | Returns WLperson(25, ("ccc", "ddd", 0), Some "Texte", Some "Texte 2") | | | Rich link formatting |
| WIKI-006 | Invalid empty link | Malformed link syntax | Parse "[[[]]]" | Returns WLnone(6, "[[[]]]") | | | Error handling |
| WIKI-007 | Invalid incomplete link | Incomplete link syntax | Parse "[[]]" | Returns WLnone(4, "[[]]") | | | Malformed input handling |
| WIKI-008 | Incomplete link start | Partial link syntax | Parse "[[w" | Returns WLnone(3, "[[w") | | | Parsing robustness |
| WIKI-009 | Page link with HTML entities | Link with special characters | Parse "[[[d_azincourt/d&#039;Azincourt]]]" | Returns WLpage with proper HTML entity handling | | | HTML entity processing |
| WIKI-010 | Mixed content parsing | Multiple links and text | Parse complex mixed content with multiple links and URLs | Returns correct sequence of WLnone and WLperson tokens | | | Complex content parsing |
| WIKI-011 | Incomplete nested link 1 | Malformed nested structure | Parse "[[[aaa/" | Returns WLnone tokens | | | Nested link handling |
| WIKI-012 | Incomplete nested link 2 | Malformed nested structure | Parse "[[[w" | Returns WLnone tokens | | | Edge case handling |
| WIKI-013 | Wizard link basic | Wizard command syntax | Parse "[[w:hg]]" | Returns WLwizard(8, "hg", "") | | | Command processing |
| WIKI-014 | Wizard link with parameter | Wizard with argument | Parse "[[w:hg/henri]]" | Returns WLwizard(14, "hg", "henri") | | | Parameterized commands |
| WIKI-015 | Nested wizard link | Complex wizard nesting | Parse "[[[[w:hg/henri]]" | Returns correct nested structure | | | Complex nesting |
| WIKI-016 | Bold/italic syntax conversion | Wiki markup to HTML | 1. Convert "abc ''def'' ghi" to HTML<br>2. Convert "abc '''def''' ghi"<br>3. Convert "abc '''''def''''' ghi" | 1. Returns "abc &lt;i&gt;def&lt;/i&gt; ghi"<br>2. Returns "abc &lt;b&gt;def&lt;/b&gt; ghi"<br>3. Returns "abc &lt;b&gt;&lt;i&gt;def&lt;/i&gt;&lt;/b&gt; ghi" | | | Text formatting |

### Genealogical Relationships (1 test)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| REL-001 | Ancestor relationship validation | Valid family tree with child, father, mother | 1. Check if father is ancestor of child<br>2. Check if child is ancestor of father<br>3. Check if mother is ancestor of child | 1. Returns true<br>2. Returns false<br>3. Returns true | | | Core genealogy logic |

### Core String and Utility Functions (15 tests)

| Test Case ID | Test Case Description | Pre-conditions | Test Steps | Expected Result | Actual Result | Status | Comments |
|--------------|----------------------|----------------|------------|-----------------|---------------|--------|----------|
| UTIL-001 | String contains substring search | Valid string inputs | Test multiple contains scenarios with "foo bar" and file paths | Returns correct boolean for each substring test | | | Core search functionality |
| UTIL-002 | String starts with validation | Valid string and position inputs | 1. Test valid positions<br>2. Test invalid positions (-1, beyond length) | 1. Returns boolean result<br>2. Raises `Invalid_argument "start_with"` | | | Input validation |
| UTIL-003 | Roman numeral conversion | Arabic numbers | Test conversions: 39↔XXXIX, 246↔CCXLVI, 421↔CDXXI, etc. | Bidirectional conversion works correctly | | | Historical numbering |
| UTIL-004 | Particle-based name comparison | Names with particles | Compare names with French particles (de, du, des, d', etc.) | Correct genealogical sorting order | | | Name sorting rules |
| UTIL-005 | Number formatting with separators | Integer input | Format numbers with comma separators | Returns "1", "10", "100", "1,000", "10,000", etc. | | | Display formatting |
| UTIL-006 | Name title capitalization | Various name formats | Capitalize "jean-baptiste" variants | Returns "Jean-Baptiste" for all variants | | | Name standardization |
| UTIL-007 | UTF-8 substring extraction | Unicode strings | Extract substrings from Japanese "日本語", Greek "ελληνικά", Slovak "švédčina" | Correct Unicode character extraction | | | International support |
| UTIL-008 | Roman numeral name conversion | Names with numbers | Convert "foo 246" to "foo CCXLVI" | Correct number-to-Roman conversion in names | | | Historical name formatting |
| UTIL-009 | UTF-8 text capitalization | Unicode strings with special chars | Capitalize various Unicode strings | Proper capitalization with international characters | | | Unicode handling |
| UTIL-010 | HTML safety processing | HTML with special characters | Process HTML with ampersands in URLs | Converts & to &#38; for safety | | | XSS prevention |
| UTIL-011 | Localized article translation | Configuration with vowels | Apply "of" translation pattern with vowel detection | Returns correctly localized text with proper articles | | | Internationalization |
| UTIL-012 | String macro processing | String with email and ampersands | Process string with email addresses and HTML entities | Returns properly formatted HTML with email links | | | Content processing |
| UTIL-013 | HTML entity escaping | Raw HTML content | Escape HTML special characters | Returns properly escaped HTML entities | | | Security processing |
| UTIL-014 | Vowel detection for articles | Various language configurations | Test vowel detection for article usage | Correct vowel detection including Unicode vowels | | | Language rules |
| UTIL-015 | Date formatting with locale | Corsican locale configuration | Format dates with Corsican month names and grammar | Returns properly localized dates: "4 d'aostu 1974", "di marzu 1974" | | | Multilingual dates |

## Notes for Python Migration

### Current Test Coverage Summary:
- **Total Tests**: 50 unit tests implemented in OCaml
- **Sosa Tests**: 6 tests covering genealogical numbering system
- **Place Tests**: 5 tests covering location management
- **Calendar Tests**: 7 tests covering date system conversions  
- **Wiki Tests**: 16 tests covering markup and link processing
- **Merge Tests**: 1 test covering family relationship logic
- **Util Tests**: 15 tests covering string processing, Unicode, HTML, and localization

### Key Business Rules Identified:
1. **Sosa Numbering**: Genealogical numbering system for ancestor tracking and generation calculation
2. **Place Standardization**: Consistent formatting with suburb notation using brackets and dashes
3. **Calendar Systems**: Support for Gregorian, Julian, French Revolutionary, and Hebrew calendars
4. **Wiki Markup**: Complex link parsing for pages, persons, and wizard commands
5. **Unicode Support**: Full international character support for global genealogy
6. **HTML Security**: Proper entity escaping to prevent XSS attacks
7. **Particle Handling**: French name particle sorting for genealogical accuracy
8. **Localization**: Multi-language support with custom lexicons and grammar rules

### Test Execution Guidelines:
- **Actual Result**: To be filled during test execution
- **Status**: Mark as Pass/Fail based on actual vs expected results  
- **Comments**: Add any observations or issues found during testing

### Priority for Python Implementation:
1. **High Priority (Core Functions)**: SOSA, PLACE, REL, UTIL-001 to UTIL-006 (genealogy fundamentals)
2. **Medium Priority (User Experience)**: CAL, WIKI, UTIL-007 to UTIL-015 (formatting and internationalization)
3. **Low Priority (Advanced Features)**: Complex wiki parsing, edge cases, template processing

### Known Issues from OCaml Implementation:
- **Calendar SDN Conversion**: Tests CAL-001 to CAL-004 are expected failures due to Calendar library limitations with incomplete dates (issue #2172)
- **Wiki Syntax**: Some wiki parsing tests are marked as known failures in CI environment

This test plan serves as both validation documentation and a roadmap for the Python migration, ensuring all 50 critical business logic tests are preserved during the transformation.
