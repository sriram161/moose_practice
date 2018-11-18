from neuron import h
class BallAndStick(object):
    """Two-section cell: A soma with active channels and
    a dendrite with passive properties."""
    def __init__(self, settings):
        self.create_sections()
        self.build_topology()
        self.build_subsets()
        geometry = settings.get('geometry')
        soma_diameter, soma_length, dend_diameter, dend_length, dend_seg = geometry
        self.define_geometry(soma_diameter, soma_length, dend_diameter, dend_length, dend_seg)
        biophysics = settings.get('biophysics')
        Ra, Cm, soma_hh_gnabar, soma_hh_gkbar, soma_hh_gl, soma_hh_el, dend_g, dend_e = biophysics
        self.define_biophysics(Ra, Cm, soma_hh_gnabar, soma_hh_gkbar, soma_hh_gl, soma_hh_el, dend_g, dend_e)
    #
    def create_sections(self):
        """Create the sections of the cell."""
        # NOTE: cell=self is required to tell NEURON of this object.
        self.soma = h.Section(name='soma', cell=self)
        self.dend = h.Section(name='dend', cell=self)
    #
    def build_topology(self):
        """Connect the sections of the cell to build a tree."""
        self.dend.connect(self.soma(1))
    #
    def define_geometry(self, soma_diameter=12.6157, soma_length=12.6157, dend_diameter=1, dend_length=200, dend_seg=5):
        """Set the 3D geometry of the cell."""
        self.soma.L = soma_length
        self.soma.diam = soma_diameter         # microns
        self.dend.L = dend_length              # microns
        self.dend.diam = dend_diameter         # microns
        self.dend.nseg = dend_seg
        h.define_shape() # Translate into 3D points.

    def define_biophysics(self, Ra=100, Cm=1, soma_hh_gnabar=0.12, soma_hh_gkbar=0.036, soma_hh_gl=0.0003, soma_hh_el=-54.3, dend_g=0.001, dend_e=-65):
        """Assign the membrane properties across the cell."""
        for sec in self.all: # 'all' defined in build_subsets
            sec.Ra = Ra    # Axial resistance in Ohm * cm
            sec.cm = Cm      # Membrane capacitance in micro Farads / cm^2
        # Insert active Hodgkin-Huxley current in the soma
        self.soma.insert('hh')
        for seg in self.soma:
            seg.hh.gnabar = soma_hh_gnabar  # Sodium conductance in S/cm2
            seg.hh.gkbar = soma_hh_gkbar  # Potassium conductance in S/cm2
            seg.hh.gl = soma_hh_gl    # Leak conductance in S/cm2
            seg.hh.el = soma_hh_el     # Reversal potential in mV
        # Insert passive current in the dendrite
        self.dend.insert('pas')
        for seg in self.dend:
            seg.pas.g = dend_g  # Passive conductance in S/cm2
            seg.pas.e = dend_e    # Leak reversal potential mV
    #
    def build_subsets(self):
        """Build subset lists. For now we define 'all'."""
        self.all = h.SectionList()
        self.all.wholetree(sec=self.soma)

    def create_syn_on_dend(self, position, e, gmax, onset, tau):
        syn = h.AlphaSynapse(self.dend(position))
        syn.e = e
        syn.gmax = gmax
        syn.onset = onset
        syn.tau = tau
        return syn

    
