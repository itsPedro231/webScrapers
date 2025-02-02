import scrapy  # type: ignore


class AdvertisingSlogansSpider(scrapy.Spider):
    """
    A Scrapy Spider designed to extract and collect advertising slogans from a specified web source.

    This spider follows links to different categories of advertising slogans and collects quotes from each category.
    It uses complex selectors (selectors3) to navigate the HTML structure and retrieves slogan information such as company name, slogan,
    and associated subcategories.

    Methods:
    --------
    parse()
        The main entry point for initiating requests to the specified web source.

    getCat(response)
        Extracts and stores categories from the response's selector.

    getSubcat(response, cat, visited)
        Follows links to subcategories within a given category and collects subcategory URLs.
        It also tracks visited URLs in a set to avoid reprocessing.

    getQuote(response, cat, subcat, visited)
        Processes individual slogan paragraphs on a page, extracting the slogan along with company information.
        It follows links to additional pages recursively until all slogans are collected.

    """

    name = "AdvertisingSlogans"

    start_urls = ["http://www.textart.ru/database/slogan/list-advertising-slogans.html"]

    def __init__(self, name=None, **kwargs):
        """
        Initialize the AdvertisingSlogans spider.

        Parameters:
            name (string, optional): The name of the spider. Defaults to None.
            \*\*kwargs: Additional keyword arguments passed to the superclass.

        Returns:
            None
        """
        super().__init__(name, **kwargs)
        self.catList = {}
        self.subCatList = []
        self.visited = set()

    def parse(self, response):
        """
        The main entry point for initiating requests to the specified web source.

        Yields:
            Response: Follows each category URL and processes it.
        """
        self.getCat(response)

        for key in self.catList.keys():
            catUrl = self.catList[key]

            yield response.follow(
                catUrl, self.getSubcat, cb_kwargs={"cat": key, "visited": []}
            )

    def getCat(self, response):
        """
        Extract and store categories from the response.

        This method uses CSS selector to find all "select[name='select3']" options
        and adds them to self.catList with their values as keys.

        Yields:
            None
        """
        for cat in response.css('select[name="select3"] option'):
            val = cat.css('::attr("value")').get()

            if val != "#":
                self.catList[cat.css("::text").get()] = val
        return

    def getSubcat(self, response, cat, visited):
        """
        Process subcategories by following their links.

        This method retrieves all subcategories from a category page,
        follows each link that points to another subcategory or main content,
        and adds the URLs to self.subCatList. It also yields responses
        for each found URL to process further.

        Yields:
            Response: Follows each subcategory or next page.
        """
        options = response.css('select[name="select3"] option')
        if options:
            for subCat in options:
                val = subCat.css('::attr("value")').get()

                if val != "#":
                    yield response.follow(
                        val,
                        self.getQuote,
                        cb_kwargs={
                            "cat": cat,
                            "subcat": subCat.css("::text").get(),
                            "visited": [],
                        },
                    )
                    self.subCatList.append(val)

        else:
            visited.append(response.request.url)
            for paragraph in response.css("p.paragraf"):
                quote = paragraph.css("span.slogan::text").get()

                if quote:
                    yield {
                        "cat": cat,
                        "subcat": None,
                        "company": paragraph.css("::text").get(),
                        "quote": paragraph.css("span.slogan::text").get(),
                    }
                next_pages = paragraph.css('a::attr("href")').getall()

                for page in next_pages:
                    if page not in visited:
                        yield response.follow(
                            page,
                            self.getQuote,
                            cb_kwargs={"cat": cat, "subcat": None, "visited": visited},
                        )
        return

    def getQuote(self, response, cat, subcat, visited):
        """
        Extract slogan information from each paragraph.

        This method iterates over each slogan paragraph in the response,
        extracts the company name and slogan text, and yields a dictionary
        containing this information. It also tracks next pages to process.

        Yields:
            dict: Contains 'cat', 'subcat', 'company', 'quote'
        """
        visited.append(response.request.url)
        for paragraph in response.css("p.paragraf"):
            quote = paragraph.css("span.slogan::text").get()

            if quote:
                yield {
                    "cat": cat,
                    "subcat": subcat,
                    "company": paragraph.css("::text").get(),
                    "quote": paragraph.css("span.slogan::text").get(),
                }
            next_pages = paragraph.css('a::attr("href")').getall()

            for page in next_pages:
                if page not in visited:
                    yield response.follow(
                        page,
                        self.getQuote,
                        cb_kwargs={"cat": cat, "subcat": subcat, "visited": visited},
                    )
        return
