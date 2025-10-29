"""Tests for Place module functionality."""

from geneweb.core.place import Place


class TestPlaceNormalization:
    """Test place name normalization functionality."""

    def test_place_name_normalization_with_brackets_and_dash(self):
        """Test PLACE-001: Place name normalization.

        Normalize "[foo-bar] - boobar (baz)" → "foo-bar, boobar (baz)"
        Handle various bracket and parenthesis formats.
        """
        # Test the primary case from the test plan
        place = Place("[foo-bar] - boobar (baz)")
        result = place.normalize()
        expected = "foo-bar, boobar (baz)"
        assert result == expected

        # Test case where opening bracket is present but not closed with dash
        place = Place("[foo-bar - boobar (baz)")
        result = place.normalize()
        expected = "[foo-bar - boobar (baz)"  # Should remain unchanged
        assert result == expected

        # Test case where brackets are present but no dash separator
        place = Place("[foo-bar] boobar (baz)")
        result = place.normalize()
        expected = "[foo-bar] boobar (baz)"  # Should remain unchanged
        assert result == expected

        # Test with different bracket content
        place = Place("[suburb] - main place")
        result = place.normalize()
        expected = "suburb, main place"
        assert result == expected

        # Test with empty brackets
        place = Place("[] - main place")
        result = place.normalize()
        expected = ", main place"
        assert result == expected

        # Test with no brackets at all
        place = Place("main place")
        result = place.normalize()
        expected = "main place"  # Should remain unchanged
        assert result == expected


class TestSuburbExtraction:
    """Test suburb extraction from place strings."""

    def test_split_place_with_different_dash_types(self):
        """Test PLACE-002: Suburb extraction from place.

        Test splitting place strings with various dash types:
        - Regular dash "-"
        - Em-dash "–"
        - En-dash "—"
        """
        # Test with regular dash (hyphen-minus)
        place = Place("[foo-bar] - boobar (baz)")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("foo-bar", "boobar (baz)")
        assert result == expected

        # Test with em-dash (U+2013)
        place = Place("[foo-bar] – boobar (baz)")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("foo-bar", "boobar (baz)")
        assert result == expected

        # Test with en-dash (U+2014)
        place = Place("[foo-bar] — boobar (baz)")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("foo-bar", "boobar (baz)")
        assert result == expected

        # Test without suburb - should return empty suburb and full place
        place = Place("boobar (baz)")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("", "boobar (baz)")
        assert result == expected

        # Test with just brackets but no dash separator
        place = Place("[foo-bar] boobar (baz)")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("", "[foo-bar] boobar (baz)")
        assert result == expected

        # Test empty input
        place = Place("")
        result = (place.get_suburb(), place.get_main_place())
        expected = ("", "")
        assert result == expected


class TestSuburbOnlyExtraction:
    """Test extracting only the suburb part from place strings."""

    def test_get_suburb_extraction(self):
        """Test PLACE-003: Suburb-only extraction.

        Extract just the suburb from place strings.
        """
        # Test with suburb present
        place = Place("[foo-bar] - boobar (baz)")
        result = place.get_suburb()
        expected = "foo-bar"
        assert result == expected

        # Test without suburb
        place = Place("boobar (baz)")
        result = place.get_suburb()
        expected = ""
        assert result == expected

        # Test with empty brackets
        place = Place("[] - main place")
        result = place.get_suburb()
        expected = ""
        assert result == expected

        # Test with empty input
        place = Place("")
        result = place.get_suburb()
        expected = ""
        assert result == expected


class TestPlaceWithoutSuburb:
    """Test extracting main place without suburb."""

    def test_get_place_without_suburb(self):
        """Test PLACE-004: Place without suburb.

        Remove suburb and return main place only.
        """
        # Test with suburb present - should return main place only
        place = Place("[foo-bar] - boobar (baz)")
        result = place.get_main_place()
        expected = "boobar (baz)"
        assert result == expected

        # Test without suburb - should return original place
        place = Place("boobar (baz)")
        result = place.get_main_place()
        expected = "boobar (baz)"
        assert result == expected

        # Test with empty input
        place = Place("")
        result = place.get_main_place()
        expected = ""
        assert result == expected

        # Test with various dash types
        place = Place("[suburb] – main place")
        result = place.get_main_place()
        expected = "main place"
        assert result == expected


class TestPlaceComparison:
    """Test place comparison for sorting functionality."""

    def test_compare_place_for_sorting(self):
        """Test PLACE-005: Place comparison for sorting.

        Compare places for correct alphabetical ordering.
        """
        # Test identical places
        place1 = Place("Paris")
        place2 = Place("Paris")
        result = place1.compare_to(place2)
        assert result == 0

        # Test different places - alphabetical order
        place1 = Place("Berlin")
        place2 = Place("Paris")
        result = place1.compare_to(place2)
        assert result < 0  # Berlin comes before Paris

        place1 = Place("Paris")
        place2 = Place("Berlin")
        result = place1.compare_to(place2)
        assert result > 0  # Paris comes after Berlin

        # Test with suburbs vs without suburbs - same main place
        place1 = Place("[Suburb] - MainCity")
        place2 = Place("MainCity")
        result = place1.compare_to(place2)
        assert result < 0  # Place with suburb should come first when main place is same

        place1 = Place("MainCity")
        place2 = Place("[Suburb] - MainCity")
        result = place1.compare_to(place2)
        assert (
            result > 0
        )  # Place without suburb should come after when main place is same

        # Test with unicode characters
        place1 = Place("Ålesund")
        place2 = Place("Berlin")
        result = place1.compare_to(place2)
        assert result > 0  # Å comes after B in Unicode sorting

        place1 = Place("café")
        place2 = Place("cafe")
        result = place1.compare_to(place2)
        assert result > 0  # Accented characters

        # Test case sensitivity
        place1 = Place("paris")
        place2 = Place("Paris")
        result = place1.compare_to(place2)
        assert result > 0  # lowercase should come after uppercase

        # Test empty strings
        place1 = Place("")
        place2 = Place("")
        result = place1.compare_to(place2)
        assert result == 0

        place1 = Place("")
        place2 = Place("Paris")
        result = place1.compare_to(place2)
        assert result < 0  # Empty string comes first

        place1 = Place("Paris")
        place2 = Place("")
        result = place1.compare_to(place2)
        assert result > 0


class TestPlaceClass:
    """Test the Place class functionality."""

    def test_place_initialization(self):
        """Test Place class initialization and automatic parsing."""
        # Test with suburb
        place = Place("[foo-bar] - boobar (baz)")
        assert place.name == "[foo-bar] - boobar (baz)"
        assert place.suburb == "foo-bar"
        assert place.main_place == "boobar (baz)"

        # Test without suburb
        place = Place("Paris")
        assert place.name == "Paris"
        assert place.suburb == ""
        assert place.main_place == "Paris"

    def test_place_normalization(self):
        """Test Place.normalize() method."""
        place = Place("[foo-bar] - boobar (baz)")
        result = place.normalize()
        assert result == "foo-bar, boobar (baz)"

        # Test case that doesn't match pattern
        place = Place("Paris")
        result = place.normalize()
        assert result == "Paris"

    def test_place_suburb_extraction(self):
        """Test Place.get_suburb() method."""
        place = Place("[foo-bar] - boobar (baz)")
        assert place.get_suburb() == "foo-bar"

        place = Place("Paris")
        assert place.get_suburb() == ""

    def test_place_main_place_extraction(self):
        """Test Place.get_main_place() method."""
        place = Place("[foo-bar] - boobar (baz)")
        assert place.get_main_place() == "boobar (baz)"

        place = Place("Paris")
        assert place.get_main_place() == "Paris"

    def test_place_comparison(self):
        """Test Place comparison methods."""
        place1 = Place("Berlin")
        place2 = Place("Paris")

        # Test compare_to method
        assert place1.compare_to(place2) < 0
        assert place2.compare_to(place1) > 0
        assert place1.compare_to(place1) == 0

        # Test comparison operators
        assert place1 < place2
        assert place2 > place1
        assert place1 == place1

        # Test with suburbs
        place_with_suburb = Place("[Suburb] - MainCity")
        place_without_suburb = Place("MainCity")

        assert place_with_suburb < place_without_suburb

    def test_place_string_representation(self):
        """Test Place string representation."""
        place = Place("[foo-bar] - boobar (baz)")
        assert str(place) == "[foo-bar] - boobar (baz)"
