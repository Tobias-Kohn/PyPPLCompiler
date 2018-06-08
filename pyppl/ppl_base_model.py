#
# This file is part of PyPPLCompiler, a compiler for probabilistic programming to create graphical models.
#
# License: GNU GPL 3 (see LICENSE.txt)
#
# 19. Mar 2018, Bradley Gram-Hansen
# 19. Mar 2018, Bradley Gram-Hansen
#
from abc import ABC, abstractmethod


class base_model(ABC):

    @abstractmethod
    def get_vertices(self):
        '''
        Generates the vertices of the graphical model.
        :return: Set of vertices
        '''
        return NotImplementedError

    @abstractmethod
    def get_vertices_names(self):
        return NotImplementedError

    @abstractmethod
    def get_arcs(self):
        return NotImplementedError

    @abstractmethod
    def get_arcs_names(self):
        return NotImplementedError

    @abstractmethod
    def get_conditions(self):
        return NotImplementedError

    @abstractmethod
    def gen_cond_vars(self):
        return NotImplementedError

    @abstractmethod
    def gen_if_vars(self):
        return NotImplementedError

    @abstractmethod
    def gen_cont_vars(self):
        return NotImplementedError

    @abstractmethod
    def gen_disc_vars(self):
        return NotImplementedError

    @abstractmethod
    def get_vars(self):
        return NotImplementedError

    @abstractmethod
    def gen_log_pdf(self, state):
        return NotImplementedError

    @abstractmethod
    def gen_log_pdf_transformed(self, state):
        return NotImplementedError

    @abstractmethod
    def gen_prior_samples(self):
        return NotImplementedError