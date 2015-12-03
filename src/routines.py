#python2
#marcustheisen@web.de

"""Basic routines for working with MCTDHB."""
from mctdhb import MCTDHB
from states import GS
from utilities import rm_output
import io_routines as io

def basic_setup(dim):
    pass

def relax(obj, tolerance=1E-8, t_tau=.1, t_max=20,
          backward=False, properties=True):
    """relax(mctdhb obj) -> GS object
    
    Find system's GroundState (GS).
    keyword arguments:
    tolerance = 1E-8 -- tolerated energy error
    t_tau = 0.1 -- working relaxation step
    max_time = 20 -- maximal time allowed for convergance
    backward = False -- backward relaxation
    properties = True -- compute GS properties
    """
    if (backward):
        obj.set_par('JOB_PREFAC', complex(+1, 0))
    else:
        obj.set_par('JOB_PREFAC', complex(-1, 0))
    if (t_tau <= 2):
        obj.set_par('TIME_TAU', t_tau)
    else:
        obj.set_par('TIME_TAU', .1)
    obj.set_par('TIME_TOLERROR_TOTAL', tolerance)
    obj.set_par('PRINT_DATA', False)    #no need to print
    obj.set_par('STATE', 1)             #relax to GS
    
    # Iterating piecewise allows feeback of converge status
    # and the internal storage binaries are kept small.
    time = 0
    time_step = 2
    obj.set_par('GUESS', 'HAND')        #first guess
    obj.set_par('TIME_BGN', time)
    obj.set_par('TIME_FNL', time_step)
    while True:
        rm_output()
        obj.run()
        print 'running'
        # Energy difference of last iteration step.
        dE = io.extract_data('NO_PR.out')[-1][obj.get_M()+3]
        if (dE < tolerance):
            print 'converged'
            break
        if (time >= t_max):
            print 'not converged'
            break
        else:
            time += time_step
            obj.set_par('GUESS', 'BINR')        #next guess
            obj.set_par('BINARY_START_POINT_T', time)
            obj.set_par('TIME_BGN', time)
            obj.set_par('TIME_FNL', time + time_step)
    
    # 'OP_PR.out' -- Operator values per particle per iteration:
    # iteration time -- [0]
    # energy constituents -- E, T, V, W [1:5]
    # x-space (3D) -- x [5:8], xx [8:11], var_x [11:14]
    # k-space (3D) -- k [14:17], kk [17:20], var_k [20:23]
    # 'NO_PR.out' Natural Occupation and Errors per iteration:
    # iteration time -- [0]
    # occupation numbers -- [1:M+1]
    # energy errors -- E, E_tolerance, dE
    data = []
    for outfile in ['OP_PR.out', 'NO_PR.out']:
        data.append(io.extract_data(outfile)[-1])
    return GS(obj, data) 

def prop(obj, tolerance=1E-6, t_final=200., backward=False, guess='BINR',
         print_step=.01):
    """Propagate the last relaxed state.
    
    keyword arguments:
    tolerance = 1E-8 -- energy tolerance
    t_final = 11 -- final time
    t_tau = .1 -- working relaxation step
    t_begin = 0 -- beginning time
    backward = False -- backward relaxation
    print_data = False -- print orb_R and CI data
    """
    if (backward):
        obj.set_par('JOB_PREFAC', complex(0, +1))
    else:
        obj.set_par('JOB_PREFAC', complex(0, -1))
    if (guess in ['BINR', 'HAND', 'DATA']):
        obj.set_par('GUESS', guess)
        obj.set_par('BINARY_START_POINT_T', obj.get_par('TIME_BGN'))
        # TODO: Adjust *.dat files.
        obj.set_par('TIME_RES_ORB_FILE_NAME', '10.0000000time.dat')
        obj.set_par('TIME_RES_CIC_FILE_NAME', '10.0000000coef.dat')
    else:
        raise Exception('Invalid guess type')
    
    obj.set_par('PRINT_DATA', True)
    obj.set_par('TIME_BGN', 0.)
    obj.set_par('TIME_FNL', t_fnl)
    obj.set_par('TIME_TAU', print_step)   #initial propagation step
    obj.set_par('TIME_PRINT_STEP', print_step)
    obj.set_par('TIME_TOLERROR_TOTAL', tolerance)
    #run
    obj.write()
    util.execute(obj.bins[0])

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
    
