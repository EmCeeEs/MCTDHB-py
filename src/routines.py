#python3.5
#marcustheisen@web.de

"""Basic routines for working with MCTDHB."""
from src.mctdhb import MCTDHB
from src.states import GS, ES
from src.utilities import rm_output
import src.io_routines as io

def basic_setup(dim):
    pass

def relax(obj, tolerance=1E-12, t_tau=.1, t_max=20,
          backward=False, LR=False):
    """relax(mctdhb obj) -> GS object
    
    Find system's GroundState (GS).
    keyword arguments:
    tolerance = 1E-12 -- tolerated energy error of relaxed state
    t_tau = 0.1 -- working relaxation step (iteration step)
    max_time = 20 -- maximal time allowed until convergance
    backward = False -- backward relaxation
    properties = True -- compute GS properties
    """
    if (backward):
        obj.set_par('JOB_PREFAC', complex(+1, 0))
    else:
        obj.set_par('JOB_PREFAC', complex(-1, 0))
    if (t_tau <= 2):
        obj.set_par('TIME_TAU', t_tau)
        obj.set_par('TIME_PRINT_STEP', t_tau)   #each iteration print data
    else:
        obj.set_par('TIME_TAU', .1)
        obj.set_par('TIME_PRINT_STEP', .1)
    obj.set_par('TIME_TOLERROR_TOTAL', tolerance)
    obj.set_par('TIME_ICI_PRT', 1)      #create as many coef data points as time data points
    obj.set_par('PRINT_DATA', False)    #no need to explicitly print *.dat
    obj.set_par('STATE', 1)             #relax to GS
    
    # Iterating piecewise allows feeback of converge status
    # and the internal storage binaries are kept small.
    time = 0
    time_step = 2
    obj.set_par('GUESS', 'HAND')        #first guess
    obj.set_par('TIME_BGN', time)
    obj.set_par('TIME_FNL', time_step + t_tau)
    while True:
        rm_output()
        obj.run()
        # Energy difference of last iteration step.
        dE = io.extract_data('NO_PR.out')[-1][obj.get_M()+4]
        print(dE)
        if (dE < tolerance):
            print('converged')
            break
        if (time >= t_max):
            print('not converged')
            raise RuntimeError
        
        time += time_step
        obj.set_par('GUESS', 'BINR')        #next guess
        obj.set_par('BINARY_START_POINT_T', time)
        obj.set_par('TIME_BGN', time)
        obj.set_par('TIME_FNL', time + time_step + t_tau)
    
    # 'OP_PR.out' -- Operator values per particle per iteration:
    # iteration time -- [0]
    # energy constituents -- E, T, V, W [1:5]
    # x-space (3D) -- x [5:8], xx [8:11], var_x [11:14]
    # k-space (3D) -- k [14:17], kk [17:20], var_k [20:23]
    # 'NO_PR.out' Natural Occupation and Errors per iteration:
    # iteration time -- [0]
    # occupation numbers -- [1:M+1]
    # energy errors -- E, E_tolerance, dE/E_tolerance, abs(dE),
    #                   abs(dE_ci), abs(dE) - abs(dE_ci)
    data = []
    for outfile in ['OP_PR.out', 'NO_PR.out']:
        data.append(io.extract_data(outfile)[-1])
    if (LR):
        return linear_response(GS(obj, data), time + time_step)
    else:
        return GS(obj, data) 

def linear_response(GS_obj, time_slice):
    """Compute MCTDHB-LR."""
    if not isinstance(GS_obj, GS):
        raise TypeError
    LR = MCTDHB()
    LR.set_par('T_FROM', time_slice)
    LR.set_par('T_TILL', time_slice)
    LR.unset_properties()
    LR.set_par('GET_LR', True)
    LR.set_par('DATA_PSI', True)
    LR.set_par('DATA_CIC', True)
    LR.set_par('LR_MAXSIL', 1000)     #this seems to affect nothing
    
    #run
    LR.run_properties()
    # 'MC_anlsplotALL.out' contains 100 LR roots:
    # root -- i + 10 + 2*M [0]
    # energies -- dE_i = E_i-E_0 [1], E_i [2]
    # norm -- orbital-, CI-part [3:5]
    # response amplitudes (RE, IM) -- f+=f-=x [5:7], x**2 [7:9]
    dpath = 'DATA/getLR/'
    state = GS_obj
    GS_root = 10 + 2*GS_obj.get_pvalue('M')
    for data in io.extract_data(dpath + 'MC_anlsplotALL.out'):
        root = data[0] - GS_root
        E = data[2] 
        norm = data[3:5]
        uAmp = data[5:7]
        gAmp = data[7:9]
        if (root > 0) and (E > GS_obj.E):
            new_state = ES(GS_obj, data)
            state.set_pright('i', new_state)
            new_state.set_pleft('i', state)
            assert (new_state.get_pvalue('i')-1 == state.get_pvalue('i')) 
            assert (state is not new_state)
            state = new_state
            assert (state is new_state)
    return GS_obj

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
    # '...time.dat' contains information about the wavefunction
    # at given time slice in real space.
    # position on grid -- (x,y,z) [0:3]
    # weight ?? -- [3]
    # potential value -- [4]
    # density -- RE/Npar IM/Npar [5:7]
    # ?? -- /weight^2/Npar [7:9]
    # orbital wavefunction -- RE, IM [9+4*(m-1), 11+4*(m-1)] for m in Morb
    # orbital ?? -- RE, IM [11+4*(m-1), 13+4*(m-1)] for m in Morb
    # natural ocuupation of m=[M,M-1,...1] -- [13+4*(M-1):13+4*(M-1)+M]
    # time slice -- [13+4*(M-1)+M]
    
    obj.set_par('PRINT_DATA', True)
    obj.set_par('TIME_BGN', 0.)
    obj.set_par('TIME_FNL', t_fnl)
    obj.set_par('TIME_TAU', print_step)   #initial propagation step
    obj.set_par('TIME_PRINT_STEP', print_step)
    obj.set_par('TIME_TOLERROR_TOTAL', tolerance)
    #run
    obj.write()
    util.execute(obj.bins[0])

def print_spec(GS_obj, Nstates=20):
    state = GS_obj
    count = 0
    while (state.get_pright('i') != None):
        print(repr(state))
        state = state.get_pright('i')
        if (count < Nstates):
            count += 1
        else:
            break
