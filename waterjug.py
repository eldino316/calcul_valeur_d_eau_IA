#!/usr/bin/env python
'''
Created on Apr 9, 2019

@author: David Braverman
'''
import sys
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__, static_folder='static')

@app.route("/", methods=['GET'])
def startup():
    '''
    Welcome page displaying input form. Prompt user for
    2 bucket capacities and a target measurement.
    Process input through calculate route.
    '''
    return render_template('form_page.html',
                           message='''This application determines how to reach a desired amount of water using two buckets of specified sizes.''')

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    '''
    Respond to browser request for favicon.
    '''
    return send_from_directory(app.static_folder, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

def log(output):
    '''
    print debug statements to stderr
    '''
    print(output, file=sys.stderr)

@app.route("/calculate", methods=['GET'])
def calculate():
    '''
    Take URL args, and determine shortest number of bucket operations to
    obtain the desired amount.
    http://localhost:5847/calculate?bucket1=34&bucket2=99&desired_amount=234&submit=Submit
    '''
    resp_data = ''
    # Sanitize input
    try:
        b1 = float(request.args['bucket1'])
        b2 = float(request.args['bucket2'])
        da = float(request.args['desiredamount'])
        bucket1 = int(round(b1))
        bucket2 = int(round(b2))
        desired_amount = int(round(da))
    except ValueError:
        resp_data = ('Only numeric values are permitted.', 403)
        return render_template('form_page.html', message=resp_data[0]), resp_data[1]
    #response_page = 'Ok'
    log('Bucket 1 is {} gallons'.format(bucket1))
    log('Bucket 2 is {} gallons'.format(bucket2))
    log('Desired Amount is {} gallons'.format(desired_amount))
    # Check for some obvious stuff
    if bucket1 + bucket2 < desired_amount:
        resp_data = ('No Solution. You need bigger buckets to achieve desired amount.', 418)
    elif bucket1 < 1:
        resp_data = ('Bucket 1 must be greater than 0', 200)
    elif bucket2 < 1:
        resp_data = ('Bucket 2 must be greater than 0', 200)
    elif  desired_amount < 1:
        resp_data = ('Desired amount must be greater than 0', 200)
    elif desired_amount % gcd(bucket1, bucket2) != 0:
        resp_data = ('Pas de solution pour cette énigme', 418)
    elif bucket1 + bucket2 == desired_amount:
        amounts = [(0, 0), (bucket1, 0), (bucket1, bucket2)]
        steps = ['les deux Carafes sont vides']
        steps.append('Fill {} gallon bucket'.format(bucket1))
        steps.append('Fill {} gallon bucket'.format(bucket2))
        return render_template('jug_output.html',
                               rows=list(zip(steps, amounts)),
                               goal=desired_amount,
                               b1name='{} Gallon Bucket'.format(bucket1),
                               b2name='{} Gallon Bucket'.format(bucket2)), 200
    #If there was an issue, tell the user and start over.
    if resp_data != '':
        return render_template('form_page.html',
                               message=resp_data[0]), resp_data[1]

    jug = WaterJug(bucket1, bucket2, desired_amount)
    steps, amounts, bucket1, bucket2 = jug.water_jug_wrapper()
    if steps is not None:
        return render_template('jug_output.html',
                               rows=list(zip(steps, amounts)),
                               goal=desired_amount,
                               b1name='{} Gal. Bucket'.format(bucket1),
                               b2name='{} Gal. Bucket'.format(bucket2)), 200

    return render_template('form_page.html', message='''An error occurred. Please check the application log.''')
def gcd(a, b):
    '''
    Return the Greatest Common Divisor for two numbers. If the desired_amount
    is not a multiple of the GCD, then there is no solution.
    '''
    if a == 0:
        return b
    return gcd(b % a, a)

class BucketBug(Exception):
    '''
    Exception for bucket pouring error.
    '''

class WaterJug():
    '''
    Calculate water jug problem in two ways: Going from small to large, and large to small.
    Return the shortest solution.
    '''
    def __init__(self, bucket1, bucket2, goal):
        if bucket1 > bucket2:
            bucket1, bucket2 = bucket2, bucket1
        self.bucket1 = bucket1
        self.bucket2 = bucket2
        self.goal = goal
        self.amounts = []
        self.steps = ['les deux Carafes sont vides']

    def water_jug_wrapper(self):
        '''
        Wrapper
        '''
        solver_bs = True
        solver_sb = True
        try:
            #self.jug_solver_SB(0,0)
            self.jug_solver(0, 0)
        except BucketBug:
            log('Exception occurred (SB):')
            log(self.steps)
            log(self.amounts)
            solver_sb = False
        #Save result and reset
        self.steps_sb = self.steps.copy()
        self.amounts_sb = self.amounts.copy()
        self.amounts = []
        self.steps = ['Both buckets are empty']
        try:
            #Swap buckets
            self.bucket1, self.bucket2 = self.bucket2, self.bucket1
            self.jug_solver(0, 0)
        except BucketBug:
            log('Exception occurred (BS):')
            log(self.steps)
            log(self.amounts)
            solver_bs = False
        self.steps_bs = self.steps
        self.amounts_bs = self.amounts

        #Some debug output for demonstration purposes
        log('Small to Large is {} steps.'.format(len(self.steps_sb)))
        log('Large to Small is {} steps.'.format(len(self.steps_bs)))
        if len(self.steps_bs) < len(self.steps_sb) and solver_bs:
            return self.steps_bs, self.amounts_bs, self.bucket1, self.bucket2
        elif solver_sb:
            return self.steps_sb, self.amounts_sb, self.bucket2, self.bucket1
        return None, None, None

    def jug_solver(self, bucket1_contents, bucket2_contents):
        '''
        Recursive function to either go from small bucket to large, or vice versa.
        '''
        self.amounts.append((bucket1_contents, bucket2_contents))
        if bucket2_contents == self.goal or bucket1_contents + bucket2_contents == self.goal:
            return
        elif bucket2_contents == self.bucket2:
            self.steps.append('vidage du {} litre carrafe'.format(self.bucket2))
            if bucket1_contents == 0:
                raise BucketBug('Solution not possible')
            self.jug_solver(bucket1_contents, 0)
        elif bucket1_contents != 0 and bucket1_contents < (self.bucket2 - bucket2_contents):
            self.steps.append('Transfer {} litre d eau au {} litre carrafe'.format(self.bucket1, self.bucket2))
            self.jug_solver(0, (bucket1_contents + bucket2_contents))
        elif bucket1_contents != 0 and bucket2_contents == 0:
            self.steps.append('Transfert de {} litre d eau au {} litre carrafe'.format(self.bucket1, self.bucket2))
            self.jug_solver(bucket1_contents-(self.bucket2 - bucket2_contents), (self.bucket2 - bucket2_contents) + bucket2_contents)
        elif bucket1_contents == self.goal:
            self.steps.append('vidage {} litre au carrafe'.format(self.bucket2))
            self.jug_solver(bucket1_contents, 0)
        elif bucket1_contents < self.bucket1:
            self.steps.append('remplissage {} litre du carrafe'.format(self.bucket1))
            self.jug_solver(self.bucket1, bucket2_contents)
        else:
            self.steps.append('Transfert de {} litre  au {} litre du carrafe'.format(self.bucket1, self.bucket2))
            self.jug_solver(bucket1_contents - (self.bucket2 - bucket2_contents),
                            (self.bucket2 - bucket2_contents) + bucket2_contents)


if __name__ == '__main__':
    log('Running on port JUGS (5847)')
    app.run(host='0.0.0.0', port=5847, debug=True, threaded=True)
