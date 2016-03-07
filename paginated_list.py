import re


class PaginatedList(object):
    """
    Abstracts `pagination of Canvas API <https://canvas.instructure.com/doc/api/file.pagination.html>`.
    """

    def __init__(self, content_class, requester, request_method, first_url, **kwargs):
        self.__elements = list()

        self.__requester = requester
        self.__content_class = content_class
        self.__first_url = first_url
        self.__first_params = kwargs or ()
        self.__first_params['per_page'] = kwargs.get('per_page', 10)
        self.__next_url = first_url
        self.__next_params = kwargs or {}

    def __getitem__(self, index):
        assert isinstance(index, (int, slice))
        if isinstance(index, (int, long)):
            self.__get_up_to_index(index)
            return self.__elements[index]
        else:
            return self._Slice(self, index)

    def __iter__(self):
        for element in self.__elements:
            yield element
        while self._has_next():
            new_elements = self._grow()
            for element in new_elements:
                yield element

    def _is_larger_than(self, index):
        return len(self.__elements) > index or self._has_next()

    def __get_up_to_index(self, index):
        while len(self.__elements) <= index and self._has_next():
            self._grow()

    def _get_last_page_url(self):
        response = self.__requester.request(
            'GET',
            self.__url,
            **self.__first_params
        )
        regex = r'%s(.*)' % (re.escape(self.__requester.base_url))
        last_link = response.links.get('last')
        self.__next_url = re.search(regex, last_link['url']).group(1) if last_link else None

    def _grow(self):
        new_elements = self._get_next_page()
        self.__elements += new_elements
        return new_elements

    def _has_next(self):
        return self.__next_url is not None

    def _get_next_page(self):
        response = self.__requester.request(
            'GET',
            self.__next_url,
            **self.__first_params
        )
        data = response.json()
        self.__next_url = None

        next_link = response.links.get('next')
        regex = r'%s(.*)' % (re.escape(self.__requester.base_url))

        self.__next_url = re.search(regex, next_link['url']).group(1) if next_link else None

        self.__next_params = None

        content = [
            self.__content_class(self.__requester, element)
            for element in data if element is not None
        ]

        return content

    def get_page(self, page):
        params = dict(self.__first_params)
        if page != 0:
            params["page"] = page + 1

        response = self.__requester.request(
            'GET',
            self.__first_url,
            **self.__first_params
        )
        data = response.json()

        return [
            self.__content_class(self.__requester, element)
            for element in data if element is not None
        ]

    class _Slice:
        def __init__(self, the_list, the_slice):
            self.__list = the_list
            self.__start = the_slice.start or 0
            self.__stop = the_slice.stop
            self.__step = the_slice.step or 1

        def __iter__(self):
            index = self.__start
            while not self.__finished(index):
                if self.__list._is_larger_than(index):
                    yield self.__list[index]
                    index += self.__step
                else:
                    return

        def __finished(self, index):
            return self.__stop is not None and index >= self.__stop
