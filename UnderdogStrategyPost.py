import numpy as np
import footballData as fd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import scipy.stats as stats
import datetime as dt

def UnderdogStrategy_Figure1():
    goal_ratios = [1.1,1.2,1.4,1.6,1.8,2]
    # for figures
    fig,ax = plt.subplots()
    col = ['b','g','k','r','c','m']
    # expected goal range for Team B (weaker Team)
    expG_TeamB = np.arange(0.2,2.1,0.1)
    for gr,c in zip(goal_ratios,col):
        # expG for Team1 = Team2 x Goal Ratio
        expG_TeamA = expG_TeamB*gr
        # probability of Team2 wining, drawing & losing
        Pw_TeamB = stats.skellam.cdf(-1,mu1=expG_TeamA,mu2=expG_TeamB)
        Pd_TeamB = stats.skellam.pmf(0,mu1=expG_TeamA,mu2=expG_TeamB)
        Pl_TeamB = 1-stats.skellam.cdf(0,mu1=expG_TeamA,mu2=expG_TeamB)
        # Team 2 expected points from encounter
        expP_TeamB = Pw_TeamB*3+Pd_TeamB
        # Exp G that maximises Team 2's expected points
        opti = expP_TeamB.argmax()
        label = 'ExpG Ratio (X) =%1.1f' % (gr)
        ax.plot(expG_TeamB,expP_TeamB,c,label=label)
        ax.plot(expG_TeamB[opti],expP_TeamB[opti],c+'o')
    ax.set_ylim(0.7,1.4)
    ax.set_xlim(0.4,2)
    ax.legend(loc='lower left', frameon=False,fontsize=9,numpoints=1)    
    ax.set_xlabel("Underdog expected goals ('Strategy')")
    ax.set_ylabel('Underdog expected points')

def QualityBalance():
    # get results for all EPL games from 2002/03 - 2016/17
    results_all = fd.read_seasons(2002,2016,"0",verbose=False)
    results_byteam = fd.get_results_all_teams(results_all)
    # seasons to evaluate
    seasons = ['0203', '0304', '0405', '0506', '0607', '0708','0809', '0910', 
               '1011', '1112', '1213', '1314', '1415', '1516','1617']
    years = np.arange(2003,2018,1)
    # get goals scored, conceded and points for every team
    scored = []
    conceded = []
    teams = []
    points = []
    for y,s in zip(years, seasons):
        # produces a league table at end of season 
        table = fd.build_season_table(results_byteam,dt.datetime(y,6,10),s)
        scored.append([t[5] for t in table])
        conceded.append([t[6] for t in table])
        teams.append([t[0] for t in table])
        points.append([t[3] for t in table])
    # some array manipulation (2D->1D)
    scored = np.array(scored).T.flatten()
    conceded = np.array(conceded).T.flatten()
    teams = np.array(teams).T.flatten()
    points = np.array(points).T.flatten()
    # normalise and rescale goals scored & conceded (and invert latter)
    scored = np.log(scored/np.mean(scored))
    conceded = -1*np.log(conceded/np.mean(conceded))
    # calculate quality and balance
    quality = scored + conceded
    balance = scored - conceded
    # check that lowest & highest 'balance' teams are the same as other analysis (they are)
    bal_inds = balance.argsort()
    print teams[bal_inds[::-1]][-10:] # most attacking
    print teams[bal_inds[::-1]][:10]
    # run regression for all teams
    Y = points
    X = np.column_stack( (np.ones_like(quality),quality,quality*balance) )
    Model1 = sm.OLS(Y,X ).fit()
    # run regression for quality<0 teams
    cut = (quality<0) # doesn't really matter if you use zero or median as divide here
    Y = points[cut]
    X = np.column_stack( (np.ones_like(quality[cut]),quality[cut],quality[cut]*balance[cut]) )
    Model2 = sm.OLS(Y,X ).fit()
    print "*** ALL TEAMS ***"
    print Model1.summary() # ALL TEAMS
    '''
==============================================================================
Dep. Variable:                      y   R-squared:                       0.935
Model:                            OLS   Adj. R-squared:                  0.935
Method:                 Least Squares   F-statistic:                     2152.
Date:                Mon, 02 Oct 2017   Prob (F-statistic):          1.82e-177
Time:                        11:34:21   Log-Likelihood:                -861.37
No. Observations:                 300   AIC:                             1729.
Df Residuals:                     297   BIC:                             1740.
Df Model:                           2                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         52.2903      0.248    210.866      0.000        51.802    52.778
slope         32.8611      0.541     60.776      0.000        31.797    33.925
interaction    6.6006      1.642      4.021      0.000         3.370     9.831
==============================================================================
Omnibus:                        1.985   Durbin-Watson:                   1.799
Prob(Omnibus):                  0.371   Jarque-Bera (JB):                1.883
Skew:                           0.194   Prob(JB):                        0.390
Kurtosis:                       3.003   Cond. No.                         6.69
==============================================================================
    '''    
    print "*** Low Quality Teams Only ***"
    print Model2.summary() # 
    '''
==============================================================================
Dep. Variable:                      y   R-squared:                       0.779
Model:                            OLS   Adj. R-squared:                  0.777
Method:                 Least Squares   F-statistic:                     303.8
Date:                Mon, 02 Oct 2017   Prob (F-statistic):           3.61e-57
Time:                        11:34:21   Log-Likelihood:                -479.96
No. Observations:                 175   AIC:                             965.9
Df Residuals:                     172   BIC:                             975.4
Df Model:                           2                                         
Covariance Type:            nonrobust                                         
==============================================================================
                 coef    std err          t      P>|t|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         51.6853      0.530     97.436      0.000        50.638    52.732
slope         30.6054      1.347     22.713      0.000        27.946    33.265
interaction    3.4084      2.547      1.338      0.183        -1.619     8.436
==============================================================================
Omnibus:                        1.362   Durbin-Watson:                   1.573
Prob(Omnibus):                  0.506   Jarque-Bera (JB):                1.409
Skew:                           0.150   Prob(JB):                        0.494
Kurtosis:                       2.679   Cond. No.                         9.81
==============================================================================   
    '''
    # Python rules.