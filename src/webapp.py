import json

from flask import Flask, render_template, request, jsonify
from SingleCntrSimulator import genCntrMasterFxp

app = Flask(__name__, template_folder='../templates', static_folder='../assets')


@app.route('/')
def index():
    '''
    This is the home page of the website, which also returns the counter bits based on counter size.
    '''
    combinedValue = ''  # Initialize the combinedValue variable
    return render_template('index.html', combinedValue=combinedValue)


@app.route('/webapp/BitstoF2P', methods=['POST'])
def bitsToF2P():
    '''
    This recieves counter size, hyper size, counter bits and flavor type from the form to return the f2p value
    it represents.
    '''
    try:
        # Retrieve the form data from the request
        cntrSize = request.form.get('cntr_size')
        hyperSize = request.form.get('hyper_size')
        cntrBits = request.form.get('cntrBits')
        flavor = request.form.get('flavor_type')
        nSystem = request.form.get('fp_type')
        signBit = cntrBits[0:1]
        sn_type=0
        snType=str(request.form.get('sn_type'))
        if snType=='signed':
            sn_type=1
        expSize    = 2**int(hyperSize)-1
        # Call the custom process_form() function
        if int(cntrSize)<3 or int(hyperSize)<1 and  sn_type==0:
             result = f'Sorry, Either number of bits or hyper-exp size is wrong!'
             return json.dumps({"result": result})
        if int(cntrSize)<4 or int(hyperSize)<1 and  sn_type==1:
             result = f'Sorry, Either number of bits or hyper-exp size is wrong!'
             return json.dumps({"result": result})
        elif sn_type==1 and expSize+int(hyperSize)<int(cntrSize):
            myCntr = genCntrMasterFxp(cntrSize=int(cntrSize)-1, hyperSize=int(hyperSize), nSystem=str(nSystem), flavor=str(flavor), verbose=[])
            if int(signBit)==0:
                result = myCntr.cntr2num(cntr=str(cntrBits[1:]))
                return json.dumps({"result": result})
            else:
                 result = -myCntr.cntr2num(cntr=str(cntrBits[1:]))
                 return json.dumps({"result": result})
        elif sn_type==0 and expSize+int(hyperSize)<int(cntrSize):
            myCntr = genCntrMasterFxp(cntrSize=int(cntrSize), hyperSize=int(hyperSize), nSystem=str(nSystem), flavor=str(flavor), verbose=[])
            result = myCntr.cntr2num(cntr=str(cntrBits))
            return json.dumps({"result": result})
        else:
            if sn_type==1:
                 result=f'For hyper-exp size {hyperSize}, the number of bits must be at least {expSize+int(hyperSize)+2}!'
                 return json.dumps({"result": result})
            else:
                result=f'For hyper-exp size {hyperSize}, the number of bits must be at least {expSize+int(hyperSize)+1}!'
                return json.dumps({"result": result})

    except Exception as e:
        # Handle any exceptions that occur during the function execution
        return json.dumps({"error": str(e)})


@app.route('/webapp/F2PtoBits', methods=['POST'])
def F2PToBits():
    '''
    This function receives counter size, hyper size, counter bits, and flavor type from the form to return the F2P value it represents.
    '''
    try:
        # Retrieve the form data from the request
        cntrSize = int(request.form.get('cntrsize'))
        hyperSize = int(request.form.get('hypersize'))
        fp_value = float(request.form.get('fpvalue'))
        flavor = str(request.form.get('flavortype'))
        nSystem = str(request.form.get('fptype'))
        snType = str(request.form.get('sntype'))
        sn_type = 1 if snType == 'signed' else 0

        expSize = 2 ** hyperSize - 1

        # Validate the input parameters
        if (sn_type == 0 and (cntrSize < 3 or hyperSize < 1)) or \
           (sn_type == 1 and (cntrSize < 4 or hyperSize < 1)):
            return {"result": "Sorry, Either the number of bits or the hyper-exponent size is invalid."}

        if sn_type == 1 and expSize + hyperSize +2 > cntrSize:
            return {"result": "The hyper-exponent size is too large for the given counter size and sign type."}
        if sn_type == 0 and expSize + hyperSize +1 > cntrSize:
            return {"result": "Sorry, The hyper-exponent size is too large for the given counter size and sign type."}

        # Generate the F2P counter and find the closest binary representation
        myCntr = genCntrMasterFxp(cntrSize=cntrSize-sn_type, hyperSize=hyperSize, nSystem=nSystem, flavor=flavor, verbose=[])

        if sn_type == 1 and fp_value < 0:
            cntr_bits = None
            for num in range(2 ** (cntrSize-1)):
                current_bits = bin(num)[2:].zfill(cntrSize-1)
                current_fp = -1 * float(myCntr.cntr2num(cntr=str(current_bits)))
                if fp_value == current_fp:
                    cntr_bits = f'1{current_bits}'
                    break
        elif sn_type == 1 and fp_value >=0:
            cntr_bits = None
            for num in range(2 ** (cntrSize-1)):
                current_bits = bin(num)[2:].zfill(cntrSize-1)
                current_fp = float(myCntr.cntr2num(cntr=str(current_bits)))
                if fp_value == current_fp:
                    cntr_bits = f'0{current_bits}'
                    break
        else:
            cntr_bits = None
            for num in range(2 ** (cntrSize)):
                current_bits = bin(num)[2:].zfill(cntrSize)
                current_fp = myCntr.cntr2num(cntr=str(current_bits))
                if fp_value == current_fp:
                    cntr_bits = f'0{current_bits}'
                    break

        if cntr_bits is None:
            return {"result": "Sorry, Could not find a suitable binary representation."}

        return {"result": cntr_bits}

    except (ValueError, TypeError):
        return {"result": "Sorry, Invalid input data."}
    except Exception as e:
        return {"result": f"{str(e)}"}


if __name__ == '__main__':
    app.run(debug=True)
