#python2
#marcustheisen@web.de

"""mctdhb_utils.py"""
def get_par_value(pars, name):
    """return parameter value"""
    name = name.upper()
    for parset in pars:
        for record in parset:
            if name in parset[record]:
                return parset[record][name]
    raise ValueError(name, 'is no MCTDHB parameter or not set')

def set_par_value(pars, name, value):
    """set parameter value"""
    name = name.upper()
    old_value = get_par_value(pars, name)
    if (type(value) is not type(old_value)):
        raise TypeError
    for record in pars:
        if name in pars[record]:
            pars[record][name] = value
            break

def set_str_par(pars, name, value):
    """set V_W_Psi parameters as string"""
    if (type(value) is not str):
        raise TypeError
    orb = ['Psi_' + str(i) + '(x_y_z)' for i in range(1, 11)]
    names = ['V(x_y_z&t)', 'W(R=|r1-r2|&t)', 'Imprint_MOM', 'Df_cnf_Fock']
    if (name in orb) or (name in names):
        pars[name] = value
    else:
        raise ValueError('unknown parameter', name)
