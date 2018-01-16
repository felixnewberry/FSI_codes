
from dolfin import *
import numpy as np
import pylab as plt
from mshr import *

# edit to make similar to chorin that works. Remove pressure BC. Rearrange fluid solver to match. Comment out previous arrangement.
# breaks after a couple of iterations ' unable to solve linear system using PETSC Krylov solver' solution failed to converge.
# breaks when mesh nodes do not align perfectly with interface. If number of discretizations is selected carefully then the code runs. Evidently
#this is a working and not elegant or long term solution. Possibly if the mesh deforms the same error will reappear.
# Therefore mesh still has to be fixed for long term solution such that fluid and structure boundaries align perfectly with mesh nodes.

########################
# when I run it with linear and E_s = 1e3. It breaks at loop iteration time 0.2.
# Mesh set to the generate_mesh  method. Norms are 8 e-08 and 4e-18.

# In the other method: Still breaks at loop iteration time 0.2. first norm is 3e-9. Marginally different.

# Ignoring precision in integral metadata compiled using quadrature representation. Not implemented.

# Problem specific section. ie lid driven cavity, or cylinder... have class generic?
class problem_specific:

	def __init__(self):
        ############## INPUT DATA PARAMETERS ###################
	    # Physical parameters
		self.nu_f = 0.001	# Fluid viscosity (was 0.2)
		self.nu_s = 0.4	# Structure Poisson coefficient should be 0.2
		self.mu_s = 0.5e6 # structure first lame constant (very small)
		#self.mu_s = 0.5e9 # structure first lame constant (very small)

		self.rho_f = 1000.0	# Fluid density (incorporated in the fluid corrected pressure as p_corr = p/rho)
		#self.rho_f = 0.001
		self.rho_s = 1000.0

		self.E_s = self.mu_s*2*(1+self.nu_s)	# structure elastic modulus
		self.lambda_s = self.nu_s*self.E_s/((1+self.nu_s)*(1-2*self.nu_s)) # 2nd lame constant

		# mean inlet velocity
		self.U_mean = 0.2

		# Numerical parameters
		self.dt = 0.001	# Time step
		#self.T = 10.00	#  Set final time for iteration
		self.T = 0.1#  Set final time for iteration
		self.N = 64		# Number of discretizations (square mesh) (place cell edge on FSI)

		# Geometric parameters
		self.L = 2.5 	#Channel length
		self.H = 0.41	#Channel height
		self.l = 0.35 	#Bar length
		self.h = 0.02	#Bar height

		#self.s_b = 2*self.h 	#Border about structure over which to refine.

		# x coordinate of start of bar
		self.x_bar = 0.6-self.l

		self.mu_f = self.rho_f*self.nu_f

		# Set up a variable for time
		self.t_vec = np.linspace(0.0,self.T,self.T/self.dt+1)
		self.t = self.t_vec[0]
		self.iter_t = 1

		################ DEFINE MESHES AND DOMAINS #######################

		self.channel = Rectangle(Point(0, 0), Point(self.L, self.H))
		# if region about cylinder is not further refined:
		#self.cylinder = Circle(Point(0.2, 0.2), 0.05, self.N*2)
		# if region is further refined:
		self.cylinder = Circle(Point(0.2, 0.2), 0.05, self.N)

		# this definition leaves bar tangent to circle with small gap
		self.bar = Rectangle(Point(self.x_bar,0.19), Point(0.6, 0.19+self.h))
		# Ensures overlap between bar and circle.
		self.bar_2 = Rectangle(Point(self.x_bar-0.01,0.19), Point(0.6, 0.19+self.h))

		# Monitor point for later use
		self.A_point = Point(0.6, 0.2)

		# fluid domain
		# appears to be a funny definition of domain. Could play round with further ideas.
		#self.f_domain = self.channel - (self.cylinder + self.bar_2) - (self.bar_2-self.bar)

		self.f_domain = self.channel - (self.cylinder + self.bar_2)

		# structure domain
		self.s_domain = self.bar

		# total domain
		#self.domain = self.channel - (self.cylinder + self.bar_2) + self.bar_2
		self.domain = self.f_domain +self.s_domain

		# Set structure as subdomain, first type for global mesh
		self.domain.set_subdomain(1,self.s_domain)
		#self.domain.set_subdomain(2,self.f_domain)

		#print self.domain.get_subdomains.__getattribute__
		#print dir(self.domain.get_subdomains.__getattribute__)
		#print dir(self.domain.has_subdomains)
		# generate global mesh

		self.mesh = generate_mesh(self.domain, self.N)

		#self.Define_Subdomains()		# Sets the subdomains and the submeshes for fluid and structure

		#fluid   = CompiledSubDomain(self.f_domain)

		#create a MeshFunction with unsigned integer values (the subdomain numbers)
		# with dimension 2, which is the cell dimension of this problem.
		#markers = MeshFunction('size_t', self.mesh, 2, self.mesh.domains())

		#markers = MeshFunction('size_t', p_s.mesh, 2, p_s.mesh.domains())

		#cell_markers = SubsetIterator(markers, 1)

		# if mesh is refined prior to submesh then submesh breaks.
		#"Mesh does not include a MeshValueCollection the cell dimension of the mesh."
		# I think this means that subdomains are not marked post refinement.

		#cell_markers = CellFunction("bool", self.mesh, False)
		#self.structure = AutoSubDomain(lambda x: x[0] >= self.x_bar and x[0] <= 0.6 and x[1] >= 0.19 and x[1] <= 0.19+self.h)		#fsi = CompiledSubDomain('on_boundary && x[0] > x_bar + DOLFIN_EPS && x[0]< L - DOLFIN_EPS && x[1]>DOLFIN_EPS && x[1] < H-DOLFIN_EPS', L = self.L, H = self.H, x_bar = self.x_bar)
		#self.structure.mark(cell_markers,True)
		#self.mesh = refine(self.mesh, cell_markers)
		#self.mesh = refine(self.mesh, cell_markers)

		# Mark subdomains anew. maybe structure as opposed to s_domain...


		# Create submesh
		self.mesh_f = SubMesh(self.mesh, 0)
		self.mesh_s = SubMesh(self.mesh, 1)

		#center = Point(0.2, 0.2)

		h_cell = self.mesh.hmin()
		#cell_f = CellFunction("bool", mesh, False)
		#for cell in cells(mesh):
		#    if cell.midpoint().distance(center) < 0.05 + h:#
		#        cell_f[cell] = True
		#mesh = refine(mesh, cell_f)

		#################### maybe try commentng out this ######################
		# define region over which to refine.
		self.struct_border = AutoSubDomain(lambda x: x[0] >= self.x_bar - DOLFIN_EPS and x[0] <= 0.6 + DOLFIN_EPS and x[1] >= 0.19 - DOLFIN_EPS and x[1] <= 0.19+self.h+DOLFIN_EPS)
		#fsi = CompiledSubDomain('on_boundary && x[0] > x_bar + DOLFIN_EPS && x[0]< L - DOLFIN_EPS && x[1]>DOLFIN_EPS && x[1] < H-DOLFIN_EPS', L = self.L, H = self.H, x_bar = self.x_bar)
		self.refine_box = AutoSubDomain(lambda x: x[0] >= 0.1 - DOLFIN_EPS and x[0] <= 0.8 + DOLFIN_EPS and x[1] >= 0.1 -DOLFIN_EPS and x[1] <= 0.3+DOLFIN_EPS)

		self.struct_border_2 = AutoSubDomain(lambda x: x[0] >= 0.2715 - DOLFIN_EPS and x[0] <= 0.6 + DOLFIN_EPS and x[1] >= 0.19 - DOLFIN_EPS and x[1] <= 0.19+self.h+DOLFIN_EPS)

		# Refine mesh on structure, fluid and whole mesh... is whole mesh ever used?
		for i_mark in range(1):
			cell_markers_1 = FacetFunction("bool", self.mesh_s, False)
			self.struct_border.mark(cell_markers_1,True)
			self.mesh_s = refine(self.mesh_s, cell_markers_1)

			cell_markers_2 = FacetFunction("bool", self.mesh, False)
			self.struct_border.mark(cell_markers_2,True)
			self.mesh = refine(self.mesh, cell_markers_2)

			cell_markers_3 = FacetFunction("bool", self.mesh_f, False)
			self.struct_border.mark(cell_markers_3,True)
			self.mesh_f = refine(self.mesh_f, cell_markers_3)

		for i_mark in range(1):
			cell_markers_1 = FacetFunction("bool", self.mesh_s, False)
			self.struct_border_2.mark(cell_markers_1,True)
			self.mesh_s = refine(self.mesh_s, cell_markers_1)

			cell_markers_2 = FacetFunction("bool", self.mesh, False)
			self.struct_border_2.mark(cell_markers_2,True)
			self.mesh = refine(self.mesh, cell_markers_2)

			cell_markers_3 = FacetFunction("bool", self.mesh_f, False)
			self.struct_border_2.mark(cell_markers_3,True)
			self.mesh_f = refine(self.mesh_f, cell_markers_3)

		# refine in a box:
		for i_mark in range(1):
			cell_markers_1 = CellFunction("bool", self.mesh_s, False)
			self.refine_box.mark(cell_markers_1,True)
			self.mesh_s = refine(self.mesh_s, cell_markers_1)

			cell_markers_2 = CellFunction("bool", self.mesh, False)
			self.refine_box.mark(cell_markers_2,True)
			self.mesh = refine(self.mesh, cell_markers_2)

			cell_markers_3 = CellFunction("bool", self.mesh_f, False)
			self.refine_box.mark(cell_markers_3,True)
			self.mesh_f = refine(self.mesh_f, cell_markers_3)



		#self.mesh_s = refine(self.mesh_s, cell_markers)
		# do I need these subdomains if I already have teh domain.set_subdomain.
		# It looks as though I could do one or the other. Try with just the above.
		#self.subdomains = CellFunction('size_t', self.mesh)
		#self.subdomains.set_all(0)

		## Sets the subdomains and the submeshes for fluid and structure
		#self.Define_Subdomains()

		self.Dim = self.mesh.topology().dim()

		# Variables to generate files
		pwd = './Results_Cylinder_FSI/'
		self.file_u_s = File(pwd + 'u_s.pvd')
		self.file_v_s = File(pwd + 'v_s.pvd')
		self.file_v_f = File(pwd + 'v_f.pvd')
		self.file_p_f = File(pwd + 'p_f.pvd')

	def compute_forces(self,Mesh,nu,u,p, ds):
		self.mesh = Mesh
		self.nu = nu
		# should include both pressure contribution and shear forces.
		# Face normals
		n = FacetNormal(self.mesh)
		# Stress tensor
		# Traction
		sigma = self.nu*(grad(u)+grad(u).T) -p*Identity(2)
		T = dot(sigma,n)

		self.drag = -T[0]*ds(3)-T[0]*ds(4)
		self.lift = -T[1]*ds(3)-T[1]*ds(4)

		# Face normals
		#n = FacetNormal(self.mesh)
		#compute force on cylinder and structure
		# F.cylinder and F.FSI are F facets 3 and 4....
		#drag = -p*n[0]*ds(1)-p*n[0]*ds(2)
		#lift = p*n[1]*ds(1)+p*n[1]*ds(2)
		self.drag1 = assemble(self.drag); self.lift1 = assemble(self.lift);
		return self.drag1, self.lift1

	def Define_Boundary_Conditions(self, S, F):

		L = self.L
		H = self.H
		h = self.h
		l = self.l
		x_bar = self.x_bar
		U_mean = self.U_mean
		############## Define boundary domain locations #################

		# It would be nice to lump walls and cylinder together.
		#inlet   = CompiledSubDomain('near(x[0], 0) && on_boundary ')
		#outlet  = CompiledSubDomain('near(x[0], L) && on_boundary', L = L)
		#walls   = CompiledSubDomain('near(x[1], 0) || near(x[1], H) && on_boundary', H = H)

		class Inlet(SubDomain):
		    def inside(self,x,on_boundary):
		        return x[0] < DOLFIN_EPS and on_boundary

		class Outlet(SubDomain):
		    def inside(self,x,on_boundary):
		        return x[0] > (L - DOLFIN_EPS) and on_boundary

		class Walls(SubDomain):
		    def inside(self,x,on_boundary):
		        return x[1] < DOLFIN_EPS and on_boundary or x[1] > H - DOLFIN_EPS and on_boundary

		# Distinguish between cylinder support and cantilver beam with fsi surface
		# Cylinder stops just short of bar.

		class Cylinder(SubDomain):
		    def inside(self,x,on_boundary):
				return x[0] > DOLFIN_EPS and x[0] < x_bar - DOLFIN_EPS and \
				x[1] > DOLFIN_EPS and x[1] < (H - DOLFIN_EPS) and on_boundary

# should FSI exclude nodes on left end? No, these nodes should have both BCs applied to them.

		class Fsi(SubDomain):
		    def inside(self,x,on_boundary):
		        return x[0] > x_bar - DOLFIN_EPS and x[0] < L - DOLFIN_EPS and \
		        x[1] > DOLFIN_EPS and x[1] < (0.19 + DOLFIN_EPS) and on_boundary or \
				x[0] > x_bar - DOLFIN_EPS and x[0] < L - DOLFIN_EPS and \
		        x[1] > (0.21 - DOLFIN_EPS) and x[1] < H - DOLFIN_EPS and on_boundary or \
				x[0] > 0.6 - DOLFIN_EPS and x[0] < L - DOLFIN_EPS and \
		        x[1] > DOLFIN_EPS and x[1] < H - DOLFIN_EPS and on_boundary

		#cylinder = CompiledSubDomain('on_boundary && x[0] > DOLFIN_EPS && x[0]< x_bar + DOLFIN_EPS && x[1]>DOLFIN_EPS && x[1] < H-DOLFIN_EPS', L = L, H = H, x_bar = x_bar)
		#fsi = CompiledSubDomain('on_boundary && x[0] > x_bar + DOLFIN_EPS && x[0]< L - DOLFIN_EPS && x[1]>DOLFIN_EPS && x[1] < H-DOLFIN_EPS', L = L, H = H, x_bar = x_bar)

		class Left(SubDomain):
		    def inside(self,x,on_boundary):
		        return x[0] > x_bar - DOLFIN_EPS and x[0] < x_bar + DOLFIN_EPS and \
		        x[1] > DOLFIN_EPS and x[1] < H - DOLFIN_EPS and on_boundary

		# Compile subdomains
		walls = Walls()
		inlet = Inlet()
		outlet = Outlet()
		cylinder = Cylinder()
		fsi = Fsi()
		left = Left()

		#inlet   = CompiledSubDomain('near(x[0], 0) && on_boundary ')
		#outlet  = CompiledSubDomain('near(x[0], L) && on_boundary', L = L)
		#walls   = CompiledSubDomain('near(x[1], 0) || near(x[1], H) && on_boundary', H = H)

		############# Initialize structure boundary #############

		# Create mesh function for Structure boundary and mark all 0
		S.cells = CellFunction("size_t", S.mesh)
		S.facets = FacetFunction("size_t", S.mesh)
		S.facets.set_all(0)

		#bottom = CompiledSubDomain('x[1] < DOLFIN_EPS && on_boundary')

		############# Initialize structure boundary #############
		# Initialize boundary objects
		S.left = left
		S.fsi = fsi

		# Mark boundaries
		# could I call this left?
		S.left.mark(S.facets, 1)
		S.fsi.mark(S.facets, 2)

		S.ds = Measure('ds', domain = S.mesh, subdomain_data = S.facets)
		S.dx = Measure('dx', domain = S.mesh, subdomain_data = S.cells)

		S.n = FacetNormal(S.mesh)

		#  BCs for the left side (no displacement)
		# Structure is in essence a cantilver beam.
		#LeftBC = DirichletBC(S.V_space, Constant((0.0, 0.0)), S.left)
		# both velocity and displacement are zero...
		LeftBC = DirichletBC(S.mixed_space, Constant((0.0, 0.0, 0.0, 0.0)), S.left)
		#LeftBC = DirichletBC(S.mixed_space.sub(0), Constant((0.0, 0.0)), S.left)

		#  Set up the boundary conditions
		S.bcs = [LeftBC]

		# Presently no BC for FSI.

		############ Initialize fluid boundary ###################

		# Create mesh function and mark all 0
		F.cells = CellFunction("size_t", F.mesh)
		F.facets = FacetFunction("size_t", F.mesh)
		F.facets.set_all(0)

		############ Initialize fluid boundary ###################

		# Initialize boundary objects
		F.inlet = inlet
		F.outlet = outlet
		F.fsi = fsi
		F.cylinder = cylinder
		F.walls = walls

		# mark boundaries for fluid
		F.inlet.mark(F.facets, 1)
		F.outlet.mark(F.facets, 2)
		F.fsi.mark(F.facets, 3)
		F.cylinder.mark(F.facets,4)
		F.walls.mark(F.facets,5)

		F.ds = Measure('ds', domain = F.mesh, subdomain_data = F.facets)
		F.dx = Measure('dx', domain = F.mesh, subdomain_data = F.cells)

		F.n = FacetNormal(F.mesh)

		#  Define  fluid boundary conditions
		noSlipwalls = DirichletBC(F.V_space, Constant((0.0, 0.0)), F.walls)
		noSlipcylinder = DirichletBC(F.V_space, Constant((0.0, 0.0)), F.cylinder)
		#  Freestream velocity boundary condition for top of cavity
		# run FSI problem:

		# Define inflow profile
		inlet_profile = ('1.5*U_mean*x[1]*(H-x[1])/pow(H/2, 2)', '0')

		bcu_inlet = DirichletBC(F.V_space, Expression(inlet_profile, H = H, U_mean = U_mean, degree=2), F.inlet)
		bcu_walls = DirichletBC(F.V_space, Constant((0, 0)), F.walls)
		bcu_cylinder = DirichletBC(F.V_space, Constant((0, 0)), F.cylinder)

		#bcu_fsi = DirichletBC(F.V_space, Constant((0, 0)), F.fsi)
		#bcu_fsi = DirichletBC(F.V_space, F.u_mesh, F.fsi)


		bcu_fsi = DirichletBC(F.V_space, F.u_mesh, F.facets, 3)
		#bc_m = [DirichletBC(F.V_space, S.v, F.facets, 3)]
		#bcu_fsi = DirichletBC(F.V_space, Constant((0, 0)), F.fsi)

		# Pressure
		# can I set this weakly?
		bcp_outlet = DirichletBC(F.S_space, Constant(0), F.outlet)

		# Set up the boundary conditions
		F.bcu = [bcu_inlet, bcu_walls, bcu_cylinder, bcu_fsi]
		F.bcp = [bcp_outlet]

# compute and save nodal values
#nodal_values_u = F.u1.vector().array()
#np.savetxt('nodal_u', nodal_values_u)
#nodal_values_p = F.p1.vector().array()
#np.savetxt('nodal_p', nodal_values_p)
#nodal_values_d = S.d_.vector().array()
#np.savetxt('nodal_d', nodal_values_d)

	def Save_Results(self, S, F):
		# Save fluid velocity and pressure
		F.u_res.assign(F.u1)
		self.file_v_f << (F.u_res, self.t)
		F.p_res.assign(F.p1)
		self.file_p_f << (F.p_res, self.t)
		#Save structure displacement and velocity
		# extract displacements and velocities for results...
		u2, v2 = S.U.split()
		# maybe like this, or maybe save U...
		self.file_u_s << (u2, self.t)
		self.file_v_s << (v2, self.t)
		#S.u_res.assign(S.u)
		#self.file_u_s << (S.u_res, self.t)
		#S.v_res.assign(S.v)
		#self.file_v_s << (S.v_res, self.t)
