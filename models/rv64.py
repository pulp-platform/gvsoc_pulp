#
# Copyright (C) 2020 ETH Zurich and University of Bologna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import gv.gvsoc_runner
import cpu.iss.iss as iss
import memory.memory as memory
from vp.clock_domain import Clock_domain
import interco.router as router
import utils.loader.loader
import gsystree as st
from interco.bus_watchpoint import Bus_watchpoint

gapy_target = True

class Soc(st.Component):

    def __init__(self, parent, name, parser):
        super().__init__(parent, name)

        [args, otherArgs] = parser.parse_known_args()
        print (args.binary)

        mem = memory.Memory(self, 'mem', size=0x1000000)

        ico = router.Router(self, 'ico')

        ico.add_mapping('mem', base=0x80000000, remove_offset=0x80000000, size=0x1000000)
        self.bind(ico, 'mem', mem, 'input')

        host = iss.Iss(self, 'host', vp_component='pulp.cpu.iss.iss_rv64')

        loader = utils.loader.loader.ElfLoader(self, 'loader', binary=args.binary)

        # RISCV bus watchpoint
        tohost = Bus_watchpoint(self, 'tohost', 0x80001000)

        self.bind(host, 'fetch', ico, 'input')
        self.bind(host, 'data', tohost, 'input')
        self.bind(tohost, 'output', ico, 'input')
        self.bind(loader, 'out', ico, 'input')
        self.bind(loader, 'start', host, 'fetchen')
        self.bind(loader, 'entry', host, 'bootaddr')



class Target(gv.gvsoc_runner.Runner):

    def __init__(self, parser, options):

        super(Target, self).__init__(parser=parser, parent=None, name='top', options=options)

        clock = Clock_domain(self, 'clock', frequency=50000000)

        soc = Soc(self, 'soc', parser)

        self.bind(clock, 'out', soc, 'clock')


    def __str__(self) -> str:
        return "RV64 virtual board"