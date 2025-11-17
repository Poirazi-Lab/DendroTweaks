# SPDX-FileCopyrightText: 2025 Poirazi Lab <dendrotweaks@dendrites.gr>
# SPDX-License-Identifier: MPL-2.0

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

    def __init__(self, type_idx, name, color) -> None:
        self._name = name
        self._type_idx = type_idx
        self._color = color
        self._sections = []


    def __repr__(self):
        return f'<Domain({self.type_idx}, {self.name}, {self.color}, {len(self.sections)} sections)>'

    def __getitem__(self, idx):
        return self._sections[idx]

    def __len__(self):
        return len(self._sections)

    def __iter__(self):
        for sec in self._sections:
            yield sec

    def __contains__(self, sec):
        return sec in self._sections


    @property
    def sections(self):
        """
        A list of sections in the domain.
        """
        return self._sections


    @property
    def name(self):
        """
        The name of the domain.
        """
        return self._name


    @property
    def type_idx(self):
        """
        The type index of the domain.
        """
        return self._type_idx

    
    @property
    def color(self):
        """
        The color of the domain.
        """
        return self._color

    
    @color.setter
    def color(self, value):
        self._color = value
        for sec in self._sections:
            for point in sec.points:
                point.domain_color = value


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
        sec._domain = self
        sec.idx_within_domain = len(self._sections)
        for point in sec.points:
            point.domain_name = self.name
            point.type_idx = self.type_idx
            point.domain_color = self.color
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
        sec._domain = None
        sec.idx_within_domain = None
        for point in sec.points:
            point.domain_name = None
            point.type_idx = None
            point.domain_color = None
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
