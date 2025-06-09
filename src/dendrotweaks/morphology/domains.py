
class Domain:
    """
    A class representing
    a morphological or functional domain in a neuron.

    Parameters
    ----------
    name : str
        The name of the domain.
    sections : List[Section], optional
        A list of sections in the domain.

    Attributes
    ----------
    name : str
        The name of the domain.
    """

    def __init__(self, name: str, sections = None) -> None:
        self.name = name
        self._sections = sections if sections else []


    def __repr__(self):
        return f'<Domain({self.name}, {len(self.sections)} sections)>'


    def __contains__(self, section):
        return section in self.sections


    @property
    def sections(self):
        """
        A list of sections in the domain.
        """
        return self._sections


    # def merge(self, other):
    #     """
    #     Merge the sections of the other domain into this domain.
    #     """
    #     self.inserted_mechanisms.update(other.inserted_mechanisms)
    #     sections = self.sections + other.sections
    #     self._sections = []
    #     for sec in sections:
    #         self.add_section(sec)


    def add_section(self, sec: "Section"):
        """
        Add a section to the domain.

        Changes the domain attribute of the section.

        Parameters
        ----------
        sec : Section
            The section to be added to the domain.
        """
        if sec in self._sections:
            warnings.warn(f'Section {sec} already in domain {self.name}.')
            return
        sec.domain = self.name
        sec.domain_idx = len(self._sections)
        self._sections.append(sec)


    def remove_section(self, sec):
        """
        Remove a section from the domain.

        Sets the domain attribute of the section
        to None.

        Parameters
        ----------
        sec : Section
            The section to be removed from the domain.
        """
        if sec not in self.sections:
            warnings.warn(f'Section {sec} not in domain {self.name}.')
            return
        sec.domain = None
        sec.domain_idx = None
        if hasattr(sec, 'path_distance_within_domain'):
            # Remove cached property if it exists
            del sec.path_distance_within_domain
        self._sections.remove(sec)


    def is_empty(self):
        """
        Check if the domain is empty.

        Returns
        -------
        bool
            True if the domain is empty, False otherwise.
        """
        return not bool(self._sections)
