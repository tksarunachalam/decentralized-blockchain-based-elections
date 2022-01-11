import json 
from web3 import Web3, HTTPProvider
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user,current_user, logout_user, login_required

from forms import LoginForm

from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

from face import final_results, check
    
app = Flask(__name__)

# configure database
app.config['SECRET_KEY']='Hello from the other side'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'    
login_manager.login_message_category = 'info'  

#Create Bcrypt instance 
bcrypt = Bcrypt(app)

app.config['FLASK_ADMIN_SWATCH'] = 'Darkly'
# admin = Admin(app, name='Electoral Officer', template_mode='bootstrap3')


# ganache blockchain address
blockchain_address = ' http://127.0.0.1:7545/'

# client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address))
# setting default account 
web3.eth.defaultAccount = web3.eth.accounts[0]

# Path to the compiled contract JSON file
compiled_contract_path = 'build/contracts/Election.json'

# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0xcCDA4F8D1B91754871b8FdE5D742fE0F036A5380'

with open(compiled_contract_path) as file:
    contract_json = json.load(file)  #load contract info as json
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions


vote_transactions = []
voted = []


@login_manager.user_loader
def load_user(vid):
    return User.query.get(int(vid))

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
    
        poll_percentage = len(voted)/len(User.query.all())
        poll_percentage = poll_percentage * 100

        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        return self.render('admin/index.html',percentage = poll_percentage, current_time = current_time)

admin = Admin(app, index_view=MyHomeView(name='Home'),template_mode='bootstrap3')



class User(db.Model, UserMixin):
    vid = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    image_file = db.Column(db.String(20), default='default.jpg')  
    password = db.Column(db.String(60), nullable=False) 
    name = db.Column(db.String, nullable=False)
    
    def get_id(self):
        return (self.vid)

    
    def __repr__(self):
        return f"Voter('{self.vid}', '{self.email}')"


admin.add_view(ModelView(User, db.session))





# stop election route 
class MyView(BaseView):
    ENDED = False
    @expose('/', methods= ['GET', 'POST'])
    def index(self):

        if current_user.get_id()!=0:          #only admin should access this page
            return redirect(url_for('home')) 
        
        else:
            web3.eth.defaultAccount = web3.eth.accounts[0]

            private_key ='a2ee7ae6dc386528812351d1c621ee9befd9cd62590470b32b455c61bc2b814bv' #private key for admin 0th account 

            # print(f'before this button {ended} ')
            if request.values.get("status") == 'stop':

                MyView.ENDED = True
                print(f'lets check the ended value here{MyView.ENDED}')
                
                # contract  = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
                # transaction = contract.functions.endElection().buildTransaction()

                # signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
                # txn_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                # txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)
                # print(txn_receipt)
            
                print(request.values.get("status"))

        return render_template('admin/stopElection.html')

admin.add_views(MyView(name='Stop Election', endpoint='stop'))

@app.route("/",methods = ['GET', 'POST'])
@app.route("/home", methods = ['GET', 'POST'])
@app.route("/login",methods = ['GET', 'POST'])
def home():

    # get the user_id and validate 
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(vid=form.voter_id.data).first()
        
        # if user and bcrypt.check_password_hash(user.password, form.password.data):
        #     login_user(user)
        #     flash('login success')
        #     return redirect(url_for('vote'))
        # else:
        #     flash('invalid Credentials', 'danger')
    if request.method == 'POST':
        vid = int(request.form.get("voter_id"))
        password = request.form.get("password")
        email = request.form.get("email")
        
        user = User.query.filter_by(vid=vid).first()
        print(user.password)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            # flash('login success', 'sucess')
            # if user.vid == 0:
            #     return redirect()
            # else:
            return redirect(url_for('face', id=vid))
        else:
            flash(f'invalid Credentials', 'danger')


    return render_template('login.html')



@app.route("/logout")
def logout():

    logout_user()
    print(current_user.get_id())
    return redirect(url_for('home'))



private_keys = ['10c2cf11da1230165361c04dcfa46a1cce0c948c93cd14b95c6b35462c12f681',  
                '4b3e3ba73f310084e6f4fc32decff017438e58225010a4a9cd0239041c2a29c3',  
               'a7c97dc5f6c655e45386c695a8cf1cb0c312cac57549ea78d487d0329adba9b8',
               '7ed732ebb32a1697ea11af538a49fa57548b7a04bfce57fd9a4cded0542aa61d',
               '72f22215b84cc8c9acd1031b827fafca13e68ef0f3664666bef20cd84552fa1e',
                '45b39958ab088e80c5379a1231ce0a4587a58bff70b9294b2c11fb4874601789',
                '7f4232a9cb0251939708f1d4ee948e02c2053db75c5127c069377c83d171eef0',
                '85669c3c1cc6a40b00eaba71d72407d94436980223f60d54482c15a4512deff7',
                '1e148f9fbc2b149c7c4e9f9138073ea68d5637d38658da4f3e5286fd63b4adeb',
                '483bc4bc8b10d2ef0d1abfddef52b6a578893223bd1fa9954f7c0b5d505e442f',
                '57fbf5268c847e6f4734d51f9d0c0f809ceaaf4802e9dbf9bef1943fe0179d13',
                '7e61b549753e1f9a0226295b3d1421ec60dc1a4af3faafe0c85cc0f01b344e86',
                '26084eea7344986d34ca30135a49e3aa272b79a70f1e0e2f5f13337b01fd9f2f',
                'bca2dae75ce46a4db107e29f63bb58336eb33aedb156f2439bc76258a5b72c1a',
                '69aaad798f0006757a0054fa8cc640eeb67c0eb4565045aa19a213c5b16f29b3',
                'e3bcbb2d0628345ab794173c2699425966d3e5e407ee3d395ecb2e0381fae361']

@login_required
@app.route("/vote", methods = ['GET', 'POST'])
def vote():
    # Fetch deployed contract reference
    contract  = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)


    # find the account address of the vote
    voter_id = current_user.get_id()
    # uncomment from this linen
    # acc = accounts[voter_id]

    # demo
        # voter_id = 6
    acc = web3.eth.accounts[voter_id]
    web3.eth.default_account =acc
    private_key = private_keys[voter_id]

    # # do this before calling the vote  function
    # web3.eth.defaultAccount = web3.eth.accounts[voter_id]
    if request.method == 'POST':

        candidate_id = int(request.form.get("radio")) - 1
        print(candidate_id)
    

        transaction = contract.functions.vote(candidate_id).buildTransaction()
        # web3 uses this count as the defualt nonce value
        transaction['nonce'] = web3.eth.getTransactionCount(acc)

        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)

        print(txn_receipt)
        flash('Voted casted')

        vote_transactions.append(txn_receipt)
        voted.append(voter_id)

    # candidates = []

    return render_template('votePage.html')


@app.route("/admin/stop", methods = ['GET', 'POST'])
def stop():
        
    return render_template('stopElection.html')


@login_required
@app.route("/delegate", methods = ['GET', 'POST'])
def delegate():

    voter_id = current_user.get_id()
    web3.eth.default_account =web3.eth.accounts[voter_id]


    if request.method =='POST':
        contract = web3.eth.contract(address = deployed_contract_address, abi = contract_abi)
        toAddress = request.form.get("address")
        transaction = contract.functions.delegation(toAddress).buildTransaction()
        transaction['nonce'] = web3.eth.getTransactionCount(web3.eth.accounts[voter_id])
        
        signed_transaction = web3.eth.account.sign_transaction(transaction, private_keys[voter_id])
        txn_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        txn_receipt = web3.eth.waitForTransactionReceipt(txn_hash)

        print(txn_receipt)
        flash(f'your Vote has been delegated', 'success')

    return render_template('delegatePage.html')    

@app.route("/result")
def results():

    voteCount = []
    position = []
    # ended = True

    ended = MyView.ENDED
    print(f'ended value {ended}' )
    if(ended):

        poll = web3.eth.contract(address = deployed_contract_address, abi = contract_abi)
        winner_name = poll.functions.winnerAnnounce().call()
        winner_name = web3.toText(winner_name)
        print(winner_name)

        # hardcode candidates
        # for cid in range(len(candidates)):
        for cid in range(7):
            votes = poll.functions.findVotesOfEachCandidate(cid).call()
            voteCount.append(votes)

    else:
        print("Election still going on!!!")

    temp = voteCount.copy()
    temp.sort(reverse=True)
    print(voteCount)
    # print(temp)
    for i in voteCount:
        position.append(temp.index(i)+1)

    print(position)

    
    
    return render_template('dummies.html', voteCount=voteCount, position=position)


@app.route("/face/<string:id>",methods = ['GET','POST'])
@login_required
def face(id):

    vid = current_user.get_id()
    user = User.query.filter_by(vid=id).first()
    voter_name = user.name #get the name of the current user

    face_name = final_results()

    print(face_name)


    # if face_name == voter_name and vid==id:    #check if the image name and the voter name is same 
    if face_name != 'Not detected ' and str(vid)==id:

        print(f' from flask {face}')
        flash(f'Welcome {voter_name} !','success')
        return redirect(url_for('vote'))

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)    







    