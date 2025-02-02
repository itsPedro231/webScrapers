class Scroller:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.current_position = 0
        self.last_position = driver.execute_script("return window.pageYOffset;")
        self.scrolling = True
        self.scroll_count = 0
        pass

    def reset(self) -> None:
        """
        Reset all scroll-related states to their initial values.
        This includes setting current_position to 0, updating last_position,
        and clearing the scrolling state.
        """
        self.current_position = 0
        self.last_position = self.driver.execute_script("return window.pageYOffset;")
        self.scroll_count = 0
        pass

    def scroll_to_top(self) -> None:
        """
        Scroll the page to the top.
        Note: This may reset the scroll_count and current_position.
        """
        self.driver.execute_script("window.scrollTo(0, 0);")
        pass

    def scroll_to_bottom(self) -> None:
        """
        Scroll the page to the bottom.
        Note: This may reset the scroll_count and current_position.
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        pass

    def update_scroll_position(self) -> None:
        """
        Update the current scroll position using the driver.
        Returns:
            float: The current scroll position in pixels.
        """
        self.current_position = self.driver.execute_script("return window.pageYOffset;")
        pass

