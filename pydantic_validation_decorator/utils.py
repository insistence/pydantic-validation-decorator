class StringUtils:
    """
    String Utils Class
    """

    @classmethod
    def is_blank(cls, string: str) -> bool:
        """Validate if the string is '' or all spaces

        Args:
            string (str): String to be validated

        Returns:
            bool: Validation results
        """
        if string is None:
            return False
        str_len = len(string)
        if str_len == 0:
            return True
        else:
            for i in range(str_len):
                if string[i] != ' ':
                    return False
            return True

    @classmethod
    def is_empty(cls, string: str) -> bool:
        """Validate if the string is '' or None

        Args:
            string (str): String to be validated

        Returns:
            bool: Validation results
        """
        return string is None or len(string) == 0
