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


from cil.utilities.projector_tests import TestCommon_ProjectionOperator_SIM
from cil.utilities.projector_tests import TestCommon_ProjectionOperator_TOY, TestCommon_ProjectionOperator
import unittest
from utils import has_gpu_tigre, has_tigre


if has_tigre:
    from cil.plugins.tigre import ProjectionOperator
    from cil.plugins.tigre import FBP

has_tigre_gpu = has_gpu_tigre()
if not has_tigre_gpu:
    print("Unable to run TIGRE GPU tests")


def setup_parameters(self):

    self.backend = 'tigre'
    self.ProjectionOperator = ProjectionOperator
    self.PO_args={'direct_method':'Siddon','adjoint_weights':'matched'}


class Test_Cone3D_Projectors_basic(unittest.TestCase, TestCommon_ProjectionOperator):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone3D()
        self.tolerance_fp=0.16


class Test_Cone3D_Projectors_sim(unittest.TestCase, TestCommon_ProjectionOperator_SIM):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone3D()
        self.tolerance_fp = 0.35


class Test_Cone3D_Projectors_toy(unittest.TestCase, TestCommon_ProjectionOperator_TOY):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone3D()
        self.tolerance_linearity = 1e-2
        self.tolerance_norm = 0.1


class Test_Cone2D_Projectors_basic(unittest.TestCase, TestCommon_ProjectionOperator):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone2D()
        self.tolerance_fp=0.16


class Test_Cone2D_Projectors_sim(unittest.TestCase, TestCommon_ProjectionOperator_SIM):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone2D()
        self.tolerance_fp = 0.2


class Test_Cone2D_Projectors_toy(unittest.TestCase, TestCommon_ProjectionOperator_TOY):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Cone2D()
        self.tolerance_linearity = 1e-2
        self.tolerance_norm = 0.1


class Test_Parallel3D_Projectors_basic(unittest.TestCase, TestCommon_ProjectionOperator):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Parallel3D()
        self.tolerance_fp=1e-5


class Test_Parallel3D_Projectors_sim(unittest.TestCase, TestCommon_ProjectionOperator_SIM):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Parallel3D()
        self.tolerance_fp = 0.25


class Test_Parallel3D_Projectors_toy(unittest.TestCase, TestCommon_ProjectionOperator_TOY):

    #@unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    @unittest.skip("TIGRE backprojector weights bug")
    def setUp(self):
        setup_parameters(self)
        self.Parallel3D()
        self.tolerance_linearity = 1e-6
        self.tolerance_norm = 1e-5


class Test_Parallel2D_Projectors_basic(unittest.TestCase, TestCommon_ProjectionOperator):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Parallel2D()
        self.tolerance_fp=1e-5


class Test_Parallel2D_Projectors_sim(unittest.TestCase, TestCommon_ProjectionOperator_SIM):

    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    def setUp(self):
        setup_parameters(self)
        self.Parallel2D()
        self.tolerance_fp = 0.15


class Test_Parallel2D_Projectors_toy(unittest.TestCase, TestCommon_ProjectionOperator_TOY):

#    @unittest.skipUnless(has_tigre_gpu, "Requires TIGRE GPU")
    @unittest.skip("TIGRE backprojector weights bug")
    def setUp(self):
        setup_parameters(self)
        self.Parallel2D()
        self.tolerance_linearity = 1e-6
        self.tolerance_norm = 1e-5

