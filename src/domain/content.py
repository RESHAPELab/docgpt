# import copy
# from typing import Any, Iterator, Literal, Self, Type

# import markdown_to_json
# import pypandoc
# import requests


from typing import TypeAlias

Content: TypeAlias = str


# class Scrapper:
#     _targets: dict[str | None, set[FileUrl]] = {}
#     _output_format: Literal["markdown"] = "markdown"

#     _last_run_errors: dict[FileUrl, Exception] = {}

#     @validate_call
#     def add_target(self, target: Target) -> Self:
#         if target.input_format not in self._targets:
#             self._targets[target.input_format] = target.urls
#         else:
#             self._targets[target.input_format].update(target.urls)

#         return self

#     def reset_targets(self) -> Self:
#         self._targets.clear()
#         return self

#     def _get_extension(self, filepath: str) -> str:
#         return filepath.strip().rsplit(".", 1)[-1]

#     def __dictify_content(
#         self,
#         content: str,
#         input_format: str,
#     ) -> OrderedDict:
#         if input_format != self._output_format:
#             content = pypandoc.convert_text(
#                 content,
#                 self._output_format,
#                 input_format,
#             )
#         return markdown_to_json.dictify(content)

#     def _get_by_url(
#         self,
#         url: FileUrl,
#         input_format: str | None = None,
#     ) -> OrderedDict[str, Any]:
#         url_str = url.unicode_string()
#         content = requests.get(url_str).text
#         if not input_format:
#             input_format = self._get_extension(url_str)

#         return self.__dictify_content(content, input_format)

#     def run(self) -> Iterator[OrderedDict[str, Any]]:
#         self._last_run_errors.clear()

#         for input_format, urls_set in self._targets.items():
#             for url in urls_set:
#                 try:
#                     yield self._get_by_url(url, input_format)
#                 except (Exception,) as e:
#                     self._last_run_errors[url] = e

#     @property
#     def run_errors(self):
#         return copy.deepcopy(self._last_run_errors)
