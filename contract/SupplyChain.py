from pyteal import *

"""Supply Chain Management"""

def approval_program():
    handle_creation = Seq([
        App.globalPut(Bytes("Count"), Int(0)),
        Return(Int(1))
    ])

    handle_optin = Return(Int(1))
    handle_closeout = Return(Int(0))
    handle_updateapp = Return(Int(0))
    handle_deleteapp = Return(Int(0))
    scratchCount = ScratchVar(TealType.uint64)
    localCount = ScratchVar(TealType.uint64)

    add_supply = Seq([
        scratchCount.store(App.globalGet(Bytes("Count"))),
        App.globalPut(Bytes("Count"), scratchCount.load() + Int(1)),
        Return(Int(1))
    ])
    add_medicine = Seq([
        localCount.store(App.localGet(Txn.sender(), Bytes("Count"))),
        App.localPut(Txn.sender(), Bytes("Count"), localCount.load() + Int(1)),
        Return(Int(1))
    ])

    halal_verify_yes = Seq([
        localCount.store(App.localGet(Txn.sender(), Bytes("Count"))),
        App.localPut(Txn.sender(), Bytes("Count"), localCount.load() + Int(1)),
        Return(Int(1))
    ])

    halal_verify_no = Seq([
        localCount.store(App.localGet(Txn.sender(), Bytes("Count"))),
        App.localPut(Txn.sender(), Bytes("Count"), localCount.load() - Int(1)),
        Return(Int(1))
    ])



    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)), 
        Cond(
            [Txn.application_args[0] == Bytes("Add_Supply"), add_supply], 
            [Txn.application_args[0] == Bytes("Add_Medicine"), add_medicine],
            [Txn.application_args[0] == Bytes("Halal_Verify_Yes"), halal_verify_yes], 
            [Txn.application_args[0] == Bytes("Halal_Verify_No"), halal_verify_no]
        )
    )


    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return compileTeal(program, Mode.Application, version=5)


def clear_state_program():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

# Write to file
appFile = open('approval.teal', 'w')
appFile.write(approval_program())
appFile.close()

clearFile = open('clear.teal', 'w')
clearFile.write(clear_state_program())
clearFile.close()
