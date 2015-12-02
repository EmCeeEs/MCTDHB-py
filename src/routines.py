#python2
#marcustheisen@web.de

"""routines.py"""

def relax(self, tolerance=1E-8,
                t_final=11.,
                t_tau=.1,
                t_begin = 0.,
                backward=False,
                print_data=False):
    """Find system's GroundState (GS)."""
    if (backward):
        self.set_par('JOB_PREFAC', complex(+1, 0))
    else:
        self.set_par('JOB_PREFAC', complex(-1, 0))
    self.set_par('PRINT_DATA', print_data)
    self.set_par('GUESS', 'HAND')
    self.set_par('STATE', 1)        #relax to GS
    self.set_par('TIME_BGN', t_begin)
    self.set_par('TIME_FNL', t_final)
    self.set_par('TIME_TOLERROR_TOTAL', tolerance)
    self.set_par('TIME_TAU', t_tau)    #working relaxation step
    self.set_par('TIME_PRINT_STEP', t_tau)
    
    m = self.get_par('MORB')
    delta_t = 5
    relaxed = False
    while not relaxed:
        self.write()
        util.execute(self.bins[0])
        # Extract data from MCTDHB outfiles.
        for name in ['NO_PR.out', 'OP_PR.out']:
            self.data[name] = io.extract_data(name)
        # Check if converged.
        #          dE(last interation)      < 'TIME_TOLERROR_TOTAL' 
        if (self.data['NO_PR.out'][-1][m+3] < tolerance):
            relaxed = True
        else:
            t_final += delta_t
            self.set_par('TIME_FNL', t_fnl)
    
    self.state = states.GS(self) 

def prop(self, backward=False,
               t_fnl=200.,
               tolerance=1E-6,
               guess='BINR',
               print_step=.01):
    """Propagate the last relaxed state."""
    if (backward):
        self.set_par('JOB_PREFAC', complex(0, +1))
    else:
        self.set_par('JOB_PREFAC', complex(0, -1))
    if (guess in ['BINR', 'HAND', 'DATA']):
        self.set_par('GUESS', guess)
        self.set_par('BINARY_START_POINT_T', self.get_par('TIME_BGN'))
        # TODO: Adjust *.dat files.
        self.set_par('TIME_RES_ORB_FILE_NAME', '10.0000000time.dat')
        self.set_par('TIME_RES_CIC_FILE_NAME', '10.0000000coef.dat')
    else:
        raise Exception('Invalid guess type')
    
    self.set_par('PRINT_DATA', True)
    self.set_par('TIME_BGN', 0.)
    self.set_par('TIME_FNL', t_fnl)
    self.set_par('TIME_TAU', print_step)   #initial propagation step
    self.set_par('TIME_PRINT_STEP', print_step)
    self.set_par('TIME_TOLERROR_TOTAL', tolerance)
    #run
    self.write()
    util.execute(self.bins[0])
    for name in ['NO_PR.out', 'OP_PR.out']:
        self.data[name] = io.extract_data(name)

def linear_response(self):
    """Compute MCTDHB-LR."""
    if (self.state is None):
        raise Exception('No relaxed state to start from.')
    self.set_par('T_FROM', self.get_par('TIME_FNL'))
    self.set_par('T_TILL', self.get_par('TIME_FNL'))
    infile = 'properties.in'
    for record in self.pars[infile]:
        for pname in self.pars[infile][record]:
            if (type(self.get_par(pname)) is bool):
                self.set_par(pname, False)
    self.set_par('GET_LR', True)
    self.set_par('DATA_PSI', True)
    self.set_par('DATA_CIC', True)
    self.set_par('LR_MAXSIL', 1000)     #this seems to affect nothing
    
    #run
    self.write()
    util.execute(self.bins[1])
    dpath = 'DATA/getLR/'
    for name in ['MC_anlsplotAll.out']:
        self.data[name] = io.extract_data(dpath + name)
    states.spec(self)
    
