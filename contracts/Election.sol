pragma solidity 0.5.16;

contract Election{

    address public electoralOfficer;

    bool Election_goingon = true;

    struct Voter{
        bool alreadyVoted;
        address delegate;
	    uint hasRecivedDelegate; 
        uint vote;
        uint weight;
    }
    struct Candidate{
        bytes32 name;
        uint votesGathered;
    }

    Candidate[] public Candidates;

    
    mapping(address => Voter) public voter_Mapping;

     constructor(bytes32[] memory candidateNames) public {
        electoralOfficer = msg.sender;
        for(uint i=0;i<candidateNames.length;i++){
            Candidates.push(
                Candidate(
                    {
                        name:candidateNames[i],
                        votesGathered: 0
                    }
                )
            );
        }
    }
    function NoOfCandidates() public view returns(uint number) {
        number = Candidates.length;
        return number;
        
    }
        
    function CheckingPermission(address voter) public{
        require(
            Election_goingon == true,
            "Election Not taking place"
        );  
        require(
            !voter_Mapping[voter].alreadyVoted,
            "Voter has alreday Voted"
        );
        // require(
        //     voter_Mapping[voter].weight == 0,
        //     "Has no right to vote"    
        // );
        //if all of the above 4 conditions satisfy allow voter to vote
        voter_Mapping[voter].weight = 1;
    	if(voter_Mapping[voter].hasRecivedDelegate>0){
    		voter_Mapping[voter].weight += voter_Mapping[voter].hasRecivedDelegate;
    	}
    }

function vote(uint candidateId) public{
        CheckingPermission(msg.sender);
        Voter storage sender = voter_Mapping[msg.sender];

        require(
            sender.weight !=0,
            "Has no right to vote"
        );
        require(
            !sender.alreadyVoted,
            "Already voted"
        );
        sender.alreadyVoted = true;
        sender.vote = candidateId;
        Candidates[candidateId].votesGathered += sender.weight;
        // Candidates[candidateId].votesGathered += 1;
    }

    function findWinningCandidate() public view returns(uint winningCandidateid){
        uint maxVoteCount = 0;
        for(uint i=0; i < Candidates.length;i++){
            if(Candidates[i].votesGathered > maxVoteCount){
                maxVoteCount = Candidates[i].votesGathered;
                winningCandidateid = i;
            }
        }
    }
    
    function findVotesOfEachCandidate(uint candidateId) public view returns(uint voteCount){
        
        voteCount = Candidates[candidateId].votesGathered;
    }

    function winnerAnnounce() public view returns(bytes32 name){
        uint id = findWinningCandidate();
        name = Candidates[id].name;
    }

    function endElection() public{
        require(
            msg.sender == electoralOfficer,
            "No access"
        );
        Election_goingon = false;
    }
    
    function startElection() public{
        Election_goingon = true;
    }

    function delegation(address to) public{
        CheckingPermission(msg.sender);
        Voter storage sender = voter_Mapping[msg.sender];
        require(
            !sender.alreadyVoted,
            "You have already voted"
        );
        require(
            to != msg.sender,
            "You can't delegate your vote to yourselves"
        );

        while(voter_Mapping[to].delegate != address(0)){
            to = voter_Mapping[to].delegate;

            require(
                to != msg.sender,
                "Looping found in delegation"
            );
        }
        sender.alreadyVoted = true;
        sender.delegate = to;
        Voter storage delegated = voter_Mapping[to];
        if(delegated.alreadyVoted){
            
            Candidates[delegated.vote].votesGathered += sender.weight;
        }
        else{
	        delegated.hasRecivedDelegate++;
            //delegated.weight += sender.weight;
        }
    }
}