# -*- coding: utf-8 -*-
#   This work is part of the Core Imaging Library (CIL) developed by CCPi 
#   (Collaborative Computational Project in Tomographic Imaging), with 
#   substantial contributions by UKRI-STFC and University of Manchester.

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from cil.optimisation.functions import Function, BlockFunction, MixedL21Norm, ZeroFunction, L2NormSquared, IndicatorBox
from cil.optimisation.operators import GradientOperator, BlockOperator,IdentityOperator, ZeroOperator, SymmetrisedGradientOperator
from cil.optimisation.algorithms import PDHG
import numpy as np


class TotalGeneralisedVariation(Function):

    r""" Total Generalised Variation (TGV) Function, see :cite:`Bredies2010`.

        .. math:: \mathrm{TGV}_{\alpha, \beta}(u) := \underset{u}{\mathrm{argmin}}\,\alpha \|\nabla u - w\|_{2,1} + \beta\|\mathcal{E}w\|_{2,1}


        Notes
        -----
        The :code:`TotalGeneralisedVariation` (TGV) :code:`Function` acts as a compositite function, i.e.,
        the composition of a separable function 
        
        .. math:: f(z_{1}, z_{2}) = f_{1}(z_{1}) + f_{2}(z_{2}) = \alpha\|z_{1}\|_{2,1} + \beta\|z_{2}\|_{2,1}


        and the operator

        .. math:: K = \begin{bmatrix}
                    \nabla & -\mathbb{I}\\
                    \mathbb{O} & \mathcal{E}
                  \end{bmatrix}
        
        Therefore, 

        .. math:: f(K \begin{bmatrix}
                       u \\
                       w 
                     \end{bmatrix}) = f_{1}(\nabla u - w) + f_{2}(\mathcal{E}w)
        

        In that case, the proximal operator of TGV does not have an exact solution and we use an iterative 
        algorithm to solve:


        .. math:: \mathrm{prox}_{\tau \mathrm{TGV}_{\alpha,\beta}}(b) := \underset{u}{\mathrm{argmin}} \frac{1}{2\tau}\|u - b\|^{2} + \mathrm{TGV_{\alpha, \beta}}(u) \Leftrightarrow

        .. math:: \underset{u,w}{\mathrm{argmin}} \frac{1}{2\tau}\|u - b\|^{2} +  \alpha \|\nabla u - w\|_{2,1} + \beta\|\mathcal{E}w\|_{2,1} 

        
        The algorithm used for the proximal operator of TGV is the Primal Dual Hybrid Algorithm, see :class:`.PDHG`.


        Parameters
        ----------
        max_iteration : :obj:`int`, default = 100
            Maximum number of iterations for the PDHG algorithm.
        correlation : :obj:`str`, default = `Space`
            Correlation between `Space` and/or `SpaceChannels` for the :class:`.GradientOperator`.
        backend :  :obj:`str`, default = `c`      
            Backend to compute the :class:`.GradientOperator`  
        split : :obj:`boolean`, default = False
            Splits the Gradient into spatial gradient and spectral or temporal gradient for multichannel data.


        Examples
        --------

        To decide


        """   
        
            
    def __init__(self,
                 alpha = 1.0,
                 beta = 2.0,
                 max_iteration = 100, 
                 correlation = "Space",
                 backend = "c",
                 split = False,
                 verbose = 0, **kwargs):
        
        super(TotalGeneralisedVariation, self).__init__(L = None)

        # regularisation parameters for TGV
        self.alpha = alpha
        self.beta = beta
                
        # Iterations for PDHG_TGV
        self.iterations = max_iteration
        
        # correlation space or spacechannels
        self.correlation = correlation

        # backend for the gradient
        self.backend = backend        
        
        # splitting Gradient
        self.split = split
                        
        # parameters to set up PDHG algorithm
        self.f1 = self.alpha * MixedL21Norm()
        self.f2 = self.beta * MixedL21Norm()
        self.f = BlockFunction(self.f1, self.f2)  
        self.g2 = ZeroFunction()

        self.verbose = verbose
        self.update_objective_interval = kwargs.get('update_objective_interval', self.iterations)


    def __call__(self, x):
        
        if not hasattr(self, 'pdhg'):   
            return 0.0        
        else:              
            # Compute alpha * || Du - w || + beta * ||Ew||, 
            # where (u,w) are solutions coming from the proximal method below.

            # An alternative option is to use 
            # self.f(self.pdhg.y_tmp) where y_tmp contains the same information as
            # self.pdhg.operator.direct(self.pdhg.solution)
            
            # However, this only works if we use pdhg.update_objective() and that means
            # that we need to compute also the adjoint operation for both Gradient and the SymmetrizedGrafientOperator.

            tmp = self.f(self.pdhg.operator.direct(self.pdhg.solution))
            return tmp
        
    def proximal(self, x, tau = 1.0, out = None):
        
        if not hasattr(self, 'domain'):
            
            # sirf "geometry"
            try:
                self.domain = x.geometry
            except:
                self.domain = x            
                        
        if not hasattr(self, 'operator'):
            
            self.Gradient = GradientOperator(self.domain, correlation = self.correlation, backend = self.backend)  
            self.SymGradient = SymmetrisedGradientOperator(self.Gradient.range, correlation = self.correlation, backend = self.backend)  
            self.ZeroOperator = ZeroOperator(self.domain, self.SymGradient.range)
            self.IdentityOperator = - IdentityOperator(self.Gradient.range)

            #    BlockOperator = [ Gradient      - Identity  ]
            #                    [ ZeroOperator   SymGradient] 
            self.operator = BlockOperator(self.Gradient, self.IdentityOperator, 
                                               self.ZeroOperator, self.SymGradient, 
                                               shape=(2,2))    

        if not all(hasattr(self, attr) for attr in ["g1", "g"]):
            self.g1 = (0.5/tau)*L2NormSquared(b = x)
            self.g = BlockFunction(self.g1, self.g2)

            
        # setup PDHG    
        
        # configure PDHG only once. This has the advantage of warm-starting in 
        # the case where this proximal method is used as an inner solver inside an algorithm.
        # That means we run .proximal for 100 iterations for one iteration of the outer algorithm,
        # and in the next iteration, we run 100 iterations of the inner solver, but we begin where we stopped before.

        
        # configure pdhg in every iteration ???         
        self.pdhg = PDHG(f = self.f, g=self.g, operator = self.operator,
                   update_objective_interval = self.update_objective_interval,
                   max_iteration = self.iterations)
        self.pdhg.run(verbose=self.verbose)
        
        # if not hasattr(self, 'pdhg'):            
        #     self.pdhg = PDHG(f = self.f, g=self.g, operator = self.operator,
        #                update_objective_interval = self.iterations,
        #                max_iteration = self.iterations)        
        # Avoid using pdhg.run() because of print messages (configure PDHG)
        # for _ in range(self.iterations):
            # self.pdhg.__next__()
        #         
        # need to reset, iteration attribute for pdhg
        # self.pdhg.iteration=0
                    
        if out is None:
            return self.pdhg.solution[0]
        else:
            out.fill(self.pdhg.solution[0])            

    def convex_conjugate(self,x):  
        
        return 0.0
    
    