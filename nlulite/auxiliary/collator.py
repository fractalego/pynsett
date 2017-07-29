class Collator:
    _delete_str = ':DELETE'

    def __init__(self, names_to_collate_forward, names_to_collate_backward):
        self.names_to_collate_forward = names_to_collate_forward
        self.names_to_collate_backward = names_to_collate_backward

    def collate(self, lst):
        lst = self.__collate_forward(lst)
        lst = self.__collate_backward(lst)
        return lst

    # Private

    def __delete_irrelevant(self, lst):
        new_lst = []
        for word in lst:
            if word.find(self._delete_str) == -1:
                new_lst.append(word)
        return new_lst

    def __collate_forward(self, lst):
        new_lst = []
        for i in range(len(lst) - 1):
            word = lst[i]
            next_word = lst[i + 1]
            new_element = word
            if word in self.names_to_collate_forward:
                new_element += next_word
                lst[i + 1] += self._delete_str
            new_lst.append(new_element)
        new_lst.append(lst[-1])
        new_lst = self.__delete_irrelevant(new_lst)
        return new_lst

    def __collate_backward(self, lst):
        new_lst = []
        for i in range(len(lst) - 1):
            word = lst[i]
            next_word = lst[i + 1]
            new_element = word
            if next_word in self.names_to_collate_backward:
                new_element = word + next_word
                lst[i + 1] += self._delete_str
            new_lst.append(new_element)
        new_lst.append(lst[-1])
        new_lst = self.__delete_irrelevant(new_lst)
        return new_lst
