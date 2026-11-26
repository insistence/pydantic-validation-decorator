class StringUtils:
    """String Utils Class."""

    @classmethod
    def is_blank(cls, string: str | None) -> bool:
        """Validate if the string is '' or all spaces.

        Args:
            string: String to be validated.

        Returns:
            Validation results.
        """
        return string is not None and all(char == ' ' for char in string)

    @classmethod
    def is_empty(cls, string: str | None) -> bool:
        """Validate if the string is '' or None.

        Args:
            string: String to be validated.

        Returns:
            Validation results.
        """
        return string is None or len(string) == 0
