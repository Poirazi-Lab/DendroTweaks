
class Domain:

    def __init__(self, name: str, sections = None) -> None:
        self.name = name
        self._sections = sections if sections else []
        # self.inserted_mechanisms = {}


    # @property
    # def mechanisms(self):
    #     return {**{'Independent': None}, **self.inserted_mechanisms}


    @property
    def sections(self):
        return self._sections


    def __contains__(self, section):
        return section in self.sections


    # def merge(self, other):
    #     """
    #     Merge the sections of the other domain into this domain.
    #     """
    #     self.inserted_mechanisms.update(other.inserted_mechanisms)
    #     sections = self.sections + other.sections
    #     self._sections = []
    #     for sec in sections:
    #         self.add_section(sec)


    # def insert_mechanism(self, mechanism):
    #     """
    #     Inserts a mechanism in the domain if it is not already inserted.

    #     Parameters
    #     ----------
    #     mechanism : Mechanism
    #         The mechanism to be inserted in the domain.
    #     """
    #     if mechanism.name in self.inserted_mechanisms:
    #         warnings.warn(f'Mechanism {mechanism.name} already inserted in domain {self.name}.')
    #         return
    #     self.inserted_mechanisms[mechanism.name] = mechanism
    #     for sec in self.sections:
    #         sec.insert_mechanism(mechanism.name)
    #     mechanism.domains[self.name] = self


    # def uninsert_mechanism(self, mechanism):
    #     """
    #     Uninserts a mechanism in the domain if it was inserted.

    #     Parameters
    #     ----------
    #     mechanism : Mechanism
    #         The mechanism to be uninserted from the domain.
    #     """
    #     if mechanism.name not in self.inserted_mechanisms:
    #         warnings.warn(f'Mechanism {mechanism} not inserted in domain {self.name}.')
    #         return
    #     self.inserted_mechanisms.pop(mechanism.name)
    #     for sec in self.sections:
    #         sec.uninsert_mechanism(mechanism.name)
    #     mechanism.domains.pop(self.name)


    def add_section(self, sec: "Section"):
        """
        Adds a section to the domain.
        Changes the domain attribute of the section.
        Inserts the mechanisms already present in the domain to the section.

        Parameters
        ----------
        sec : Section
            The section to be added to the domain.
        """
        if sec in self._sections:
            warnings.warn(f'Section {sec} already in domain {self.name}.')
            return
        sec.domain = self.name
        # for mech_name in self.inserted_mechanisms:
        #     sec.insert_mechanism(mech_name)
        self._sections.append(sec)


    def remove_section(self, sec):
        if sec not in self.sections:
            warnings.warn(f'Section {sec} not in domain {self.name}.')
            return
        sec.domain = None
        # for mech_name in self.inserted_mechanisms:
        #     sec.uninsert_mechanism(mech_name)
        self._sections.remove(sec)


    def is_empty(self):
        return not bool(self._sections)


    # def to_dict(self):
    #     return {
    #         # 'mechanisms': list(self.mechanisms.keys()),
    #         'sections': [sec.idx for sec in self.sections]
    #     }


    def __repr__(self):
        return f'<Domain({self.name}, {len(self.sections)} sections)>'
