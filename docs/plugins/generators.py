import lxml.html
import markdown
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File


class IndexGeneratorPlugin(BasePlugin):
    """A MkDocs plugin that generates the index.

    Make sure it comes after any other file generators.
    """

    def on_config(self, config):
        self.config = config

    def on_files(self, files, config):
        self.files = files
        self.exists = any(file.name == "index" for file in files)
        if not self.exists:
            files.append(
                File(
                    "index.md",
                    config["docs_dir"],
                    config["site_dir"],
                    config["use_directory_urls"],
                )
            )

    def on_page_read_source(self, _, page, config):
        if self.exists or page.file.name != "index":
            return
        source_lines = []
        with open("../README.md", encoding="utf-8") as file:
            readme_html = markdown.markdown(file.read(), extensions=["mdx_partial_gfm"])
        readme_root = lxml.html.fromstring(readme_html)
        source_lines.append(self.get_title(readme_root))
        source_lines.append(self.get_description(readme_root))

        source_lines.append("## Table of Contents")
        pages = [file.page for file in self.files.documentation_pages()]
        for page in pages[: pages.index(page)]:  # Exclude unpopulated pages
            source_lines.append(f"### [{page.title}]({page.url})")
            root = lxml.html.fromstring(page.content)
            source_lines.append(self.get_description(root))
            source_lines.append(self.get_toc(page.markdown))
        return "\n".join(source_lines)

    def get_title(self, root):
        title_element = root.xpath("/html/div/h1[1]")[0]
        return lxml.html.tostring(title_element, encoding="unicode")

    def get_description(self, root):
        description_elements = root.xpath(
            "/html/div/h2[1]/preceding-sibling::*[not(self::h1)]"
        )
        return "\n".join(
            lxml.html.tostring(element, encoding="unicode")
            for element in description_elements
        )

    def get_toc(self, source):
        toc_config = {"toc": {}}
        md = markdown.Markdown(
            extensions=self.config["markdown_extensions"],  # toc is builtin
            extension_configs={**self.config["mdx_configs"], **toc_config},
        )
        md.convert(source)
        toc_root = lxml.html.fromstring(md.toc)
        toc_element = toc_root.xpath("/html/body/div/ul/li[1]/ul")[0]
        return lxml.html.tostring(toc_element, encoding="unicode")


class ChangelogGeneratorPlugin(BasePlugin):
    def on_files(self, files, config):
        self.exists = any(file.name == "changelog" for file in files)
        if not self.exists:
            files.append(
                File(
                    "changelog.md",
                    config["docs_dir"],
                    config["site_dir"],
                    config["use_directory_urls"],
                )
            )

    def on_page_read_source(self, _, page, config):
        if self.exists or page.file.name != "changelog":
            return
        with open("../CHANGELOG.md", encoding="utf-8") as file:
            return file.read()
