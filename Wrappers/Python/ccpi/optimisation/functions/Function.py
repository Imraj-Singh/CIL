# -*- coding: utf-8 -*-
#========================================================================
# Copyright 2019 Science Technology Facilities Council
# Copyright 2019 University of Manchester
#
# This work is part of the Core Imaging Library developed by Science Technology
# Facilities Council and University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#=========================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import warnings

from numbers import Number
from ccpi.optimisation.operators import ZeroOperator, Identity

class Function(object):
    
    """ Abstract class representing a function 
    
        :param L: Lipschitz constant of the gradient of the function F(x), when it is differentiable.
        :param domain: The domain of the function.

    """
    
    
    def __init__(self, domain = None, L = None):
        
        self.L = L
        self.domain = domain

    def __call__(self,x):
        
        r"""Returns the value of the function F at x: :math:`F(x)`
        
        """        
        
        raise NotImplementedError

    def gradient(self, x, out=None):
        
        r"""Returns the value of the gradient of function F at x, if it is differentiable
        
        .. math:: F'(x)
        
        """
        raise NotImplementedError

    def proximal(self, x, tau, out=None):
        
        r"""Returns the proximal operator of function :math:`\tau * F` at x
        
        .. math:: \mathrm{prox}_{\tau F}(x) = \underset{z}{\mathrm{argmin}} \frac{1}{2}\|z - x\|^{2} + \tau F(z)
                
        """
        raise NotImplementedError

    def convex_conjugate(self, x):
        r""" Returns the convex conjugate of function :math:`F` at :math:`x^{*}`,
        
        .. math:: F^{*}(x^{*}) = \underset{x^{*}}{\sup} <x^{*}, x> - F(x)
                
        """
        raise NotImplementedError

    def proximal_conjugate(self, x, tau, out = None):
        
        r"""Returns the proximal operator of the convex conjugate of function :math:`\tau F` at :math:`x^{*}`
        
        .. math:: \mathrm{prox}_{\tau F^{*}}(x^{*}) = \underset{z^{*}}{\mathrm{argmin}} \frac{1}{2}\|z^{*} - x^{*}\|^{2} + \tau F^{*}(z^{*})
        
        Due to Moreau’s identity, we have an analytic formula to compute the proximal operator of the convex conjugate :math:`F^{*}`
        
        .. math:: \mathrm{prox}_{\tau F^{*}}(x) = x - \tau\mathrm{prox}_{\tau^{-1} F}(\tau^{-1}x)
                
        """
        if out is None:
            return x - tau * self.proximal(x/tau, 1/tau)
        else:            
            self.proximal(x/tau, 1/tau, out = out)
            out*=-tau
            out.add(x, out = out) 

    def grad(self, x):
        """Alias of gradient(x,None)"""
        warnings.warn('''This method will disappear in following 
        versions of the CIL. Use gradient instead''', DeprecationWarning)
        return self.gradient(x, out=None)

    def prox(self, x, tau):
        """ Alias of proximal(x, tau, None)"""
        warnings.warn('''This method will disappear in following 
        versions of the CIL. Use proximal instead''', DeprecationWarning)
        return self.proximal(x, tau, out=None)
    
    def domain(self):
        """  Returns the domain of the function :math:`F`. 
        Although, it is mathematically correct to setup a function based on the domain, 
        we do not use this information at the moment. """
        return self.domain
    
    # Algebra for Function Class
    
        # Add functions
        # Subtract functions
        # Add/Substract with Scalar
        # Multiply with Scalar
    
    def __add__(self, other):
        
        """ Returns the sum of the functions.
        
            Cases: a) the sum of two functions :math:`(F_{1}+F_{2})(x) = F_{1}(x) + F_{2}(x)`
                   b) the sum of a function with a scalar :math:`(F_{1}+scalar)(x) = F_{1}(x) + scalar`

        """
        
        if isinstance(other, Function):
            return SumFunction(self, other)
        elif isinstance(other, (SumFunctionScalar, ConstantFunction, Number)):
            return SumFunctionScalar(self, other)
        else:
            raise ValueError('Not implemented')   
            
    def __radd__(self, other):
        
        """ Making addition commutative. """
        return self + other 
                          
    def __sub__(self, other):
        """ Returns the subtraction of the functions."""
        return self + (-1) * other    

    def __rmul__(self, scalar):
        """Returns a function multiplied by a scalar."""               
        return ScaledFunction(self, scalar)
    
    def __mul__(self, scalar):
        """ Returns a function multiplied by a scalar from the left."""                    
        return scalar * ScaledFunction(self, 1)   
    
    def centered_at(self, center):
        """ Returns a translated function, namely if we have a function :math:`F(x)` the center is at the origin. 
        
            TranslateFunction is :math:`F(x - b)` and the center is at point b."""
        return TranslateFunction(self, center)  
    
class SumFunction(Function):
    
    """ SumFunction represents the sum of two functions
    
    .. math:: (F_{1} + F_{2})(x)  = F_{1}(x) + F_{2}(x)
    
    """
    
    def __init__(self, function1, function2 ):
                
        super(SumFunction, self).__init__()        

        #if function1.domain != function2.domain:            
        #    raise ValueError('{} is not the same as {}'.format(function1.domain, function2.domain)) 
            
        #self.domain = function1.domain
                                
        if function1.L is not None and function2.L is not None:
            self.L = function1.L + function2.L
            
        self.function1 = function1
        self.function2 = function2               
            
    def __call__(self,x):
        r"""Returns the value of the sum of functions :math:`F_{1}` and :math:`F_{2}` at x
        
        .. math:: (F_{1} + F_{2})(x) = F_{1}(x) + F_{2}(x)
        
        """  
        return self.function1(x) + self.function2(x)
    
    def gradient(self, x, out=None):
        
        r"""Returns the value of the sum of the gradient of functions :math:`F_{1}` and :math:`F_{2}` at x, 
        if both of them are differentiable
        
        .. math:: (F'_{1} + F'_{2})(x)  = F'_{1}(x) + F'_{2}(x)
        
        """
        
#        try: 
        if out is None:            
            return self.function1.gradient(x) +  self.function2.gradient(x)  
        else:
            out_tmp = out.copy()
            out_tmp *=0
            self.function1.gradient(x, out=out)
            self.function2.gradient(x, out=out_tmp)
            out_tmp.add(out, out=out)
#            out.add(self.function2.gradient(x, out=out), out=out)
#        except NotImplementedError:
#            print("Either {} or {} is not differentiable".format(type(self.function1).__name__), type(self.function1).__name__)) 
                            
            
        
class ScaledFunction(Function):
    
    """ScaledFunction

    A class to represent the scalar multiplication of an Function with a scalar. 
    It holds a function and a scalar. Basically it returns the multiplication
    of the product of the function __call__, convex_conjugate and gradient with the scalar.
    For the rest it behaves like the function it holds.

    Args:
       function (Function): a Function or BlockOperator
       scalar (Number): a scalar multiplier
    Example:
       The scaled operator behaves like the following: ewfwefwfefw
       
    """
    def __init__(self, function, scalar):
        
        super(ScaledFunction, self).__init__() 
                                                     
        if not isinstance (scalar, Number):
            raise TypeError('expected scalar: got {}'.format(type(scalar)))
        
        if function.L is not None:        
            self.L = abs(scalar) * function.L  
            
        self.scalar = scalar
        self.function = function       
              
    def __call__(self,x, out=None):
        '''Evaluates the function at x '''
        return self.scalar * self.function(x)

    def convex_conjugate(self, x):
        '''returns the convex_conjugate of the scaled function '''
        return self.scalar * self.function.convex_conjugate(x/self.scalar)
    
    def gradient(self, x, out=None):
        '''Returns the gradient of the function at x, if the function is differentiable'''
        
#        try:
        if out is None:            
            return self.scalar * self.function.gradient(x)
        else:
            self.function.gradient(x, out=out)
            out *= self.scalar  
#        except NotImplementedError:
#            print("{} is not differentiable".format(type(self.function).__name__))                         

    def proximal(self, x, tau, out=None):
        '''This returns the proximal operator for the function at x, tau
        '''
#        if out is None:
        return self.function.proximal(x, tau*self.scalar, out=out)     
#        else:
#            self.function.proximal(x, tau*self.scalar, out = out)

#    def proximal_conjugate(self, x, tau, out = None):
#        '''This returns the proximal operator for the function at x, tau
#        '''
#        if out is None:
#            return self.scalar * self.function.proximal_conjugate(x/self.scalar, tau/self.scalar)
#        else:
#            self.function.proximal_conjugate(x/self.scalar, tau/self.scalar, out=out)
#            out *= self.scalar

    def function(self):
        return self.function

class SumFunctionScalar(SumFunction):
          
    """ SumFunctionScalar represents the sum a function with a scalar. 
    
        .. math:: (F + scalar)(x)  = F(x) + scalar
    
        Although SumFunction has no general expressions for 
        
        i) convex_conjugate
        ii) proximal
        iii) proximal_conjugate
            
        if the second argument is a ConstantFunction then we can derive the above analytically.
    
    """    
    
    def __init__(self, function, constant):
        
        super(SumFunctionScalar, self).__init__(function, ConstantFunction(constant))        
        self.constant = constant
        self.function = function
        
    def convex_conjugate(self,x):
        
        r""" Returns the convex conjugate of a :math:`(F+scalar)`
                
        .. math:: (F+scalar)^{*}(x^{*}) = F^{*}(x^{*}) - scalar
                        
        """        
        return self.function.convex_conjugate(x) - self.constant
    
    def proximal(self, x, tau, out=None):
        
        """ Returns the proximal operator of :math:`F+scalar`

        .. math:: \mathrm{prox}_{\tau (F+scalar)}(x) = \mathrm{prox}_{\tau F}
                        
        """                
        return self.function.proximal(x, tau, out=out)        
            
    def function(self):       
       return self.function    

class ConstantFunction(Function):
    
            
    r""" ConstantFunction: :math:`F(x) = constant, constant\in\mathbb{R}`         
        
    """
    
    def __init__(self, constant = 0):
        
        super(ConstantFunction, self).__init__(L=0)
        
        if not isinstance (constant, Number):
            raise TypeError('expected scalar: got {}'.format(type(constant)))
                
        self.constant = constant
              
    def __call__(self,x):
        
        """ Returns the value of the function, :math:`F(x) = constant`"""
        return self.constant
        
    def gradient(self, x, out=None):
        
        """ Returns the value of the gradient of the function, :math:`F'(x)=0`"""       
        
        return ZeroOperator(x.geometry).direct(x, out=out)
    
    def convex_conjugate(self, x):
                        
        """ The convex conjugate of constant function :math:`F(x) = constant\in\mathbb{R}` is
        
        .. math:: 
            F(x^{*}) 
            =
            \begin{cases}
                -constant, & if x^{*} = constant\\
                \infty, & \mbox{otherwise}
            \end{cases}
                                                          
                    
        However, :math:`x^{*} = constant` only in the limit of iterations, so in fact this can be infinity.
        We do not want to have inf values in the convex conjugate, so we have to penalise this value accordingly.
        The following penalisation is useful in the PDHG algorithm, when we compute primal & dual objectives
        for convergence purposes.
        
        .. math:: F^{*}(x^{*}) = \sum \max\{x^{*}-b, 0\}
        
        """               
        return (x-self.constant).maximum(0).sum()
                
    def proximal(self, x, tau, out=None):
        
        """Returns the proximal operator of the constant function, which is the same element, i.e.,
        
        .. math:: \mathrm{prox}_{\tau F}(x) = x 
        
        """
        
        return Identity(x.geometry).direct(x, out=out)

class ZeroFunction(ConstantFunction):
    
    """ ZeroFunction represents the zero function, :math:`F(x) = 0`        
    """
    
    def __init__(self):
        super(ZeroFunction, self).__init__(constant = 0.) 
        
class TranslateFunction(Function):
    
    r"""TranslateFunction: Let function :math:`F(x)`, we consider :math:`F( x - b)`
                                
    """
    
    def __init__(self, function, center):
        
        super(TranslateFunction, self).__init__(L = function.L) 
                        
        self.function = function
        self.center = center
        
        '''
            slope should be DataContainer
        
        '''
        
    def __call__(self, x):
        
        return self.function(x - self.center)
    
    def gradient(self, x, out = None):
        
        if out is None:
            return self.function.gradient(Identity(x.geometry).direct(x) - self.center)
        else:            
            Identity(x.geometry).direct(x, out = out)
            out.subtract(self.center, out = out)
            self.function.gradient(out, out = out)           
    
    def proximal(self, x, tau, out = None):
        
        if out is None:
            return self.function.proximal(x - self.center, tau) + self.center
        else:                    
            x.subtract(self.center, out = out)
            self.function.proximal(out, tau, out = out)
            out.add(self.center, out = out)
                    
    def convex_conjugate(self, x):
        
        return self.function.convex_conjugate(x) + self.center.dot(x)
                 
    def function(self):       
       return self.function             

#### Do we want it????
#class IndicatorSingleton(Function):
#    
#    """ Indicator funtion for the singleton C = {0}
#        
#    """
#    
#    def __init__(self, constant = 0):
#        
#        super(IndicatorSingleton, self).__init__()
#        
#    def __call__(self):
#        pass
#                
#    def convex_conjugate(self):
#        pass
#    
#    def proximal_conjugate(self):
#        pass
    