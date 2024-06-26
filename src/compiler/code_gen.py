from phase import *
if(userChoice2=="y"):
	debug5 = True
else:
	debug5 = False
code = ""
firstSymbol = ''
genBy = ""

def findFunc(func, symbolTable):            #search for function with name func and return the symbol table of that function
    global debug5
    r = ProcEntry();
    toReturn = {};
    if(debug5):
        print "printing func ", func
    for id in symbolTable.symbolDictionary: 
        if(type(r)==type(symbolTable.symbolDictionary[id])):  
            if symbolTable.symbolDictionary[id].procName == func :   #if this entry's name is func, return this entry's pointer(symboltable)
                #toReturn['symbolTable'] = symbolTable.symbolDictionary[id].pointer;
                #toReturn['procEntry'] = symbolTable.symbolDictionary[id];
                return (symbolTable.symbolDictionary[id].pointer, symbolTable.symbolDictionary[id])
                return toReturn;
            else:
                flag = findFunc(func,symbolTable.symbolDictionary[id].pointer)  #search within this function's symbol table. if function found, return the symbol table found, else continue with loop
                if(flag):
                    return flag
    return False

instrSize = 4;
defaultFrameSize = 32;
table = SymbolTable()
funcReturnType = 'INTEGER'
funcFrameSize = 0
funcEntry = None
funcStack = []
def translate(quad, procname, label):
    #global code;
    #if(quad.op=='BEGIN_FUNC' or quad.op=='END_FUNC'):
    global symbolTable
    global debug5
    global table
    global funcReturnType
    global funcFrameSize
    global funcEntry
    tempCode = ''
    if(debug5):
        print "printing procname ", procname
    if(quad.op == 'BEGIN_FUNC' or quad.op == 'END_FUNC' or procname != ''):
        
        if(quad.op == 'BEGIN_FUNC' or quad.op == 'END_FUNC'):
            if(debug5):
                print "Printing symb tab"
                symbolTable.Print()
                print "quad.arg1 ", quad.arg1
            (table, funcEntry) = findFunc(quad.arg1, symbolTable)    #find symboltable of the function and the procentry of the function
            #print "function : ", quad.arg1
            
            if(debug5):
                print "TABLE KA OFFSET!!", table.offset
            funcFrameSize = table.offset            #space for local variables
            #now, you'll be able to access global variable of offset t using $sp(frameSize - 2*instrsize - offset OR frameSize - instrsize - offset , depending on whether there is a return value)
            
            
            j = 1
            '''for i in funcEntry.type:                #space for arguments (only if # of arguments > 4)
                if(j>4):
                    if(i=='INTEGER'):
                        funcFrameSize += intSize
                    elif(i=='REAL'):
                        funcFrameSize += realSize
                j+=1
            '''
            
            funcReturnType= funcEntry.returnType 
            
            funcFrameSize += instrSize          #for storing the fp 
            if(funcReturnType):
                #print "function with return type ", funcReturnType
                funcFrameSize += instrSize                                  #for storing the return address
            else:
                #print "no return type " 
                pass
            if(debug5):
                print funcFrameSize
            funcFrameSize = ((funcFrameSize/defaultFrameSize)+1)*defaultFrameSize
            
            assemblyOffset = funcFrameSize - instrSize          #stores where the next thing is to be stored (wrt sp)
            
            
            
            if(quad.op == 'BEGIN_FUNC'):
                funcStack.append([quad.arg1, funcFrameSize, len(funcEntry.type)])
                if(debug5):
                    print "pushing func ! ", funcStack, "  ", label
                    print "hello!"
                tempCode += quad.arg1+":\n"
                tempCode += "subu $sp, $sp, "+str(funcFrameSize)+"\n"
                tempCode += 'move $s0, $sp\n'
                if(funcReturnType):
                    
                    tempCode+="sw $ra, " + str(assemblyOffset)  +"($sp)\n"
                    assemblyOffset -= instrSize
                
                tempCode+="sw $fp, "+ str(assemblyOffset) +"($sp)\n"        #save frame pointer
                assemblyOffset -= instrSize
                
                tempCode+="addu $fp, $sp, "+str(funcFrameSize)+"\n"
                
                if(debug5):
                    print "printing tempcode ", tempCode
            elif(quad.op=='END_FUNC'):
                if(debug5):
                    print "ending function!!!"
                if(funcReturnType):
                    tempCode += "lw $ra, "+ str(assemblyOffset) +"($sp)\n"      #reload saved registers, and add sp, jump to return address
                    assemblyOffset -= instrSize
                tempCode += "lw $fp, "+ str(assemblyOffset) + "($sp)\n"
                assemblyOffset -= instrSize
                
                tempCode+="addu $sp, $sp, " + str(funcFrameSize) + "\n"
                tempCode += 'lw $s0, ($sp)\n'
                tempCode += 'addu $sp, $sp, 4\n'
                tempCode += "addu $sp, $sp, "+str(instrSize*len(funcEntry.type))+'\n'
                tempCode+="jr $ra\n"
                
                funcStack.pop()
                if(debug5):
                    print "pushing func ! ", funcStack
        else:
            arg1offset = 0 
            arg2offset = 0
            resultoffset = 0
            arg1Location = 0
            arg2Location = 0
            resultLocation = 0
            flag1 = 0
            flag2 = 0
            flag3 = 0
            flag11 = 0
            flag12 = 0
            flag13 = 0
            var = VarEntry()
            if(quad.op=='+' or quad.op=='-' or quad.op=='*' or quad.op=='DIV' or quad.op =='MOD' or quad.op=='/' or quad.op in relOps):
                for id in table.symbolDictionary:
                    entry = table.symbolDictionary[id]
                    if(entry.id == quad.arg1):
                        if(entry.offset < instrSize*len(funcEntry.type)):
                            arg1Location = funcFrameSize + entry.offset + instrSize
                            flag1 = 1 
                        else:
                            arg1offset= entry.offset - instrSize*len(funcEntry.type)
                        flag11 = 1
                    if(entry.id == quad.arg2):
                        if(entry.offset < instrSize*len(funcEntry.type)):
                            arg2Location = funcFrameSize + entry.offset+ instrSize
                            flag2 = 1
                        else:
                            arg2offset= entry.offset  - instrSize*len(funcEntry.type)
                        flag12 = 1
                    if(entry.id == quad.result):
                        if(debug5):
                            print "printing some stuff ", entry.offset
                        if(entry.offset < instrSize*len(funcEntry.type)):
                            resultLocation = funcFrameSize + entry.offset+ instrSize
                            if(debug5):
                                print "address : ", resultLocation
                            flag3 = 1
                        else:
                            resultoffset= entry.offset - instrSize*len(funcEntry.type)
                        flag13 = 1
                        
                if(funcReturnType):
                    if(flag1==0 and flag11==1):
                        arg1Location = funcFrameSize - 3*instrSize - arg1offset 
                    if(flag2==0 and flag12==1):
                        arg2Location = funcFrameSize - 3*instrSize - arg2offset
                    if(flag3==0 and flag13==1):
                        resultLocation = funcFrameSize - 3*instrSize - resultoffset
                else:
                    if(flag1==0 and flag11==1):
                        arg1Location = funcFrameSize - 2*instrSize - arg1offset
                    if(flag2==0 and flag12==1):
                        arg2Location = funcFrameSize - 2*instrSize - arg2offset
                    if(flag3==0 and flag13==1):
                        resultLocation = funcFrameSize - 2*instrSize - resultoffset
                        
                 
            elif(quad.op=='READINT' or quad.op=='READREAL'  or quad.op is None or quad.op=='param' or quad.op=='return' or quad.op in unaryOps or quad.op=='ifgoto' or quad.op=='retval'):
                for id in table.symbolDictionary:
                    entry = table.symbolDictionary[id]
                    if(type(entry)==type(var)):
                        if(entry.id == quad.arg1):
                            if(entry.offset < instrSize*len(funcEntry.type)):
                                arg1Location = funcFrameSize + entry.offset+ instrSize
                                flag1 = 1
                            else:
                                arg1offset= entry.offset - instrSize*len(funcEntry.type)
                            if(debug5):
                                print "HAAAAAAAAAAA"
                            flag11=1
                        if(entry.id == quad.result and quad.op!='return'):
                            if(entry.offset < instrSize*len(funcEntry.type)):
                                resultLocation = funcFrameSize + entry.offset+ instrSize
                                flag3 = 1
                            else:
                                resultoffset= entry.offset - instrSize*len(funcEntry.type)
                            flag13=1
                            
                if(funcReturnType):
                    if(flag1==0 and flag11==1):
                        arg1Location = funcFrameSize - 3*instrSize - arg1offset
                    #arg2Location = funcFrameSize - 3*instrSize - arg2offset
                    if(quad.op is None or quad.op in unaryOps):
                        if(flag3==0 and flag13 == 1):
                            resultLocation = funcFrameSize - 3*instrSize - resultoffset
                else:
                    if(flag1==0 and flag11==1):
                        arg1Location = funcFrameSize - 2*instrSize - arg1offset
                    #arg2Location = funcFrameSize - 3*instrSize - arg2offset
                    if(quad.op is None or quad.op in unaryOps):
                        if(flag3==0 and flag13 == 1):
                            resultLocation = funcFrameSize - 2*instrSize - resultoffset
                
            
            
            if(debug5):
                print "PRINTING FLAG11!!! ", flag11
                     
            if(quad.op=='+'):
                if(quad.opType == 'INTEGER'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1, '+ str(quad.arg1) +'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                    tempCode += 'add $t0,$t1,$t2 \n';
                    
                    if(flag13==1):
                        tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t0, _' + quad.result  + '\n'
                    
                elif(quad.opType == 'REAL'):
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    
                    if(type(quad.arg2) == type(1.0)):
                        tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'l.s $f2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                    tempCode += 'add.s $f0,$f1,$f2 \n';
                    
                    if(flag13==1):
                        tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f0, _' + quad.result  + '\n'
                    #tempCode += 's.s $f0,_'+quad.result+'\n';        
                     
                    
                    #tempCode += 'sw $t0,'+str(resultLocation)+'($s0)\n';
                    
                    
            elif(quad.op=='-'):
                if(quad.opType == 'INTEGER'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1, '+ str(quad.arg1) +'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                    tempCode += 'sub $t0,$t1,$t2 \n';
                    
                    if(flag13==1):
                        tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t0, _' + quad.result  + '\n'
                    
                elif(quad.opType == 'REAL'):
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    
                    if(type(quad.arg2) == type(1.0)):
                        tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'l.s $f2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                    tempCode += 'sub.s $f0,$f1,$f2 \n';
                    
                    if(flag13==1):
                        tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f0, _' + quad.result  + '\n'       
                    

                    
                
            elif(quad.op=='*'):
                if(quad.opType == 'INTEGER'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1, '+ str(quad.arg1) +'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(quad.arg2=='i'):
                            print "printing stuff ", flag12
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                    tempCode += 'mul $t0,$t1,$t2 \n';
                    
                    if(flag13==1):
                        tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t0, _' + quad.result  + '\n'
                    
                    #tempCode += 'sw $t0,_'+quad.result+'\n';
                    
                
                elif(quad.opType == 'REAL'):
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    
                    if(type(quad.arg2) == type(1.0)):
                        tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'l.s $f2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                    tempCode += 'mul.s $f0,$f1,$f2 \n';
                    
                    if(flag13==1):
                        tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f0, _' + quad.result  + '\n'       
                    
                    
                    
            elif(quad.op=='DIV'):
                if(quad.opType == 'INTEGER'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1, '+ str(quad.arg1) +'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                    tempCode += 'div $t1,$t2 \n';
                    tempCode += 'mflo $t0\n';
                    
                    
                    if(flag13==1):
                        tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t0, _' + quad.result  + '\n'
                
                
                
            elif(quad.op=='MOD'):
                if(quad.opType == 'INTEGER'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1, '+ str(quad.arg1) +'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                    tempCode += 'div $t1,$t2 \n';
                    tempCode += 'mfhi $t0\n';
                    
                    
                    if(flag13==1):
                        tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t0, _' + quad.result  + '\n'
                
            elif(quad.op=='/'):
                
                if(quad.opType == 'REAL'):
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    
                    if(type(quad.arg2) == type(1.0)):
                        tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'l.s $f2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                    tempCode += 'div.s $f0,$f1,$f2 \n';
                    
                    if(flag13==1):
                        tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f0, _' + quad.result  + '\n'       
                    
                
            
            elif(quad.op in relOps):
                if(debug5):
                    print "Entered relOps", quad.Print(-1)
                if(quad.opType=='INTEGER'):
                    if(debug5):
                        print "Entered integer relOps"
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n';
                        #tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                    if(type(quad.arg2) == type(1)):
                        tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'lw $t2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'lw $t1, '+str(arg2Location)+'($s0)\n';
                        #tempCode += 'lw $t2, _'+quad.arg2+'\n';
                        
                        
                    if(quad.op=='<'):
                        tempCode += 'blt $t1, $t2, _'+str(quad.result)+'\n'
                    elif(quad.op=='<='):
                        tempCode += 'ble $t1, $t2, _'+str(quad.result)+'\n'
                    elif(quad.op=='>'):
                        tempCode += 'bgt $t1, $t2, _'+str(quad.result)+'\n'
                    elif(quad.op=='>='):
                        tempCode += 'bge $t1, $t2, _'+str(quad.result)+'\n'
                    elif(quad.op=='='):
                        tempCode += 'beq $t1, $t2, _'+str(quad.result)+'\n'
                    elif(quad.op=='#'):
                        tempCode += 'bne $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.opType=='REAL'):
                    if(debug5):
                        print "Entered real relOps"
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'l.s $f1, '+str(arg1Location)+'($s0)\n';
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    if(type(quad.arg2) == type(1.0)):
                        tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                    else:
                        if(flag12==1):
                            tempCode += 'l.s $f2, ' + str(arg2Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f2, _' + quad.arg2  + '\n'
                        
                        #tempCode += 'l.s $f2, '+str(arg2Location)+'($s0)\n';
                        #tempCode += 'l.s $f2, _'+quad.arg2+'\n';
                    if(quad.op=='<'):
                        tempCode += 'c.lt.s $f1, $f2 \n'
                        tempCode += 'bc1t _'+str(quad.result)+'\n';
                    elif(quad.op=='<='):
                        tempCode += 'c.le.s $f1, $f2 \n'
                        tempCode += 'bc1t _'+str(quad.result)+'\n';
                    elif(quad.op=='>'):
                        tempCode += 'c.le.s $f1, $f2 \n'
                        tempCode += 'bc1f _'+str(quad.result)+'\n';
                    elif(quad.op=='>='):
                        tempCode += 'c.lt.s $f1, $f2 \n'
                        tempCode += 'bc1f _'+str(quad.result)+'\n';
                    elif(quad.op=='='):
                        tempCode += 'c.eq.s $f1, $f2 \n';
                        tempCode += 'bc1t _'+str(quad.result)+'\n'
                    elif(quad.op=='#'):
                        tempCode += 'c.eq.s $f1, $f2 \n';
                        tempCode += 'bc1f _'+str(quad.result)+'\n'             
            
            elif(quad.op in unaryOps):
                if(debug5):
                    print "Entered unaryOps", quad.Print(-1)
                if(quad.op == 'intToReal'):
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n';
                        #tempCode += 'lw $t1, _'+quad.arg1+'\n';
                    tempCode += 'mtc1 $t1, $f0 \n';
                    tempCode += 'cvt.s.w $f0, $f0\n';    
                    if(flag13==1):
                        tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f0, _' + quad.result  + '\n'
                    
                    #tempCode += 's.s $fo, '+str(resultLocation)+'($s0)\n';
                    #tempCode += 's.s $f0,_'+quad.result+'\n';   
                elif(quad.opType=='INTEGER'):
                    if(debug5):
                        print "Entered integer unaryOps"
                    if(type(quad.arg1) == type(1)):
                        tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                        
                        tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n';
                        #tempCode += 'lw $t1, _'+quad.arg1+'\n';
                    if(quad.op=='UMINUS'):
                         tempCode += 'neg $t0, $t1\n'
                         if(flag13==1):
                            tempCode += 'sw $t0, ' + str(resultLocation) + ' ($s0) \n'
                         else:
                            tempCode += 'sw $t0, _' + quad.result  + '\n'
                        
                         #tempCode += 'sw $t0, '+str(resultLocation)+'($s0)\n';
                         #tempCode += 'sw $t0,_'+quad.result+'\n';
                    elif(quad.op=='UPLUS'):
                         #tempCode += 'sw $t1,_'+quad.result+'\n';
                         if(flag13==1):
                            tempCode += 'sw $t1, ' + str(resultLocation) + ' ($s0) \n'
                         else:
                            tempCode += 'sw $t1, _' + quad.result  + '\n'
                            
                         #tempCode += 'sw $t1, '+str(resultLocation)+'($s0)\n';
                elif(quad.opType=='REAL'):
                    if(debug5):
                        print "Entered real unaryOps";
                    if(type(quad.arg1) == type(1.0)):
                        tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    else:
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'l.s $f1, '+str(arg1Location)+'($s0)\n';
                        
                        #tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                    if(quad.op=='UMINUS'):
                         tempCode += 'neg.s $f0, $f1\n'
                         if(flag13==1):
                            tempCode += 's.s $f0, ' + str(resultLocation) + ' ($s0) \n'
                         else:
                            tempCode += 's.s $f0, _' + quad.result  + '\n'
                        
                         #tempCode += 's.s $f0, '+str(resultLocation)+'($s0)\n';
                         #tempCode += 's.s $f0,_'+quad.result+'\n';
                    elif(quad.op=='UPLUS'):
                         #tempCode += 's.s $f1,_'+quad.result+'\n';
                         if(flag13==1):
                            tempCode += 's.s $f1, ' + str(resultLocation) + ' ($s0) \n'
                         else:
                            tempCode += 's.s $f1, _' + quad.result  + '\n'
                        
                         #tempCode += 's.s $f1, '+str(resultLocation)+'($s0)\n';
            elif(quad.op=='goto'):
                tempCode += 'b _'+str(quad.result)+'\n'
            elif(quad.op=='ifgoto'):
                if(flag11==1):
                    tempCode += 'lw $t0, ' + str(arg1Location) + ' ($s0) \n'
                else:
                    tempCode += 'lw $t0, _' + quad.arg1  + '\n'
                
                #tempCode += 'lw $t0, '+str(arg1Location)+'($s0)\n'
                
                tempCode += 'beq $t0,1, _'+str(quad.result)+'\n'
            
            
            elif(quad.op == 'READINT'):
                tempCode += 'li $v0 , 5\n';
                tempCode += 'syscall\n';
                
                if(flag11==1):
                    tempCode += 'sw $v0, ' + str(arg1Location) + ' ($s0) \n'
                else:
                    tempCode += 'sw $v0, _' + quad.arg1  + '\n'
                
                #tempCode += 'sw $v0, _'+str(quad.arg1)+'\n';
            elif(quad.op == 'READREAL'):
                tempCode += 'li $v0 , 6\n';
                tempCode += 'syscall\n';
                
                if(flag11==1):
                    tempCode += 's.s $f0, ' + str(arg1Location) + ' ($s0) \n'
                else:
                    tempCode += 's.s $f0, _' + quad.arg1  + '\n'
                #tempCode += 's.s $f0, _'+str(quad.arg1)+'\n';       
                
            
            
            elif(quad.op is None):
                if(quad.arg1=='retval'):
                    if(quad.opType!='REAL'):
                       reg = '$v0'
                    else:
                        reg = '$f0'
                        
                    #tempCode += 'addu $s0, $s0, 4\n'
                    if(quad.opType!='REAL'):
                    
                        if(flag13==1):
                            tempCode += 'sw ' + reg+  ', ' + str(resultLocation) + ' ($s0) \n'
                        else:
                            tempCode += 'sw '+reg+  ', _' + quad.result  + '\n'
                    else:
                        if(flag13==1):
                            tempCode += 's.s ' + reg+  ', ' + str(resultLocation) + ' ($s0) \n'
                        else:
                            tempCode += 's.s '+reg+  ', _' + quad.result  + '\n'
                        
                    #tempCode += 'sw $v0, '+str(resultLocation)+'($s0)\n'
                
                elif(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                    if(flag13==1):
                        tempCode += 'sw $t1, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t1, _' + quad.result  + '\n'
                elif(type(quad.arg1)==type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                    if(flag13==1):
                        tempCode += 's.s $f1, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 's.s $f1, _' + quad.result  + '\n'
                
                    #tempCode += 'sw $t1,'+str(resultLocation)+'($s0)\n';
                #elif(type(quad.arg1) == type(1.0)):
                #    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                #    tempCode += 's.s $f1,_'+quad.result+'\n';
                elif(quad.arg1==True):
                    tempCode += 'li $t1, 1\n';
                    if(flag13==1):
                        tempCode += 'sw $t1, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t1, _' + quad.result  + '\n'
                    
                    #tempCode += 'sw $t1,'+str(resultLocation)+'($s0)\n';
                elif(quad.arg1==False):
                    tempCode += 'li $t1, 0\n';
                    if(flag13==1):
                        tempCode += 'sw $t1, ' + str(resultLocation) + ' ($s0) \n'
                    else:
                        tempCode += 'sw $t1, _' + quad.result  + '\n'
                    #tempCode += 'sw $t1,'+str(resultLocation)+'($s0)\n';
                else:
                    if(quad.opType=='REAL'):
                        if(flag11==1):
                            tempCode += 'l.s $f1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s $f1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n'; 
                        if(flag13==1):
                            tempCode += 's.s $f1, ' + str(resultLocation) + ' ($s0) \n'
                        else:
                            tempCode += 's.s $f1, _' + quad.result  + '\n'
                    else:
                        if(flag11==1):
                            tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                        
                        #tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n'; 
                        if(flag13==1):
                            tempCode += 'sw $t1, ' + str(resultLocation) + ' ($s0) \n'
                        else:
                            tempCode += 'sw $t1, _' + quad.result  + '\n'
                    
                    #tempCode += 'sw $t1, '+str(resultLocation)+'($s0)\n';
            elif(quad.op=='param'):
            #elif(quad.op=='param'):
                if(quad.opType == 'STRING'):
                    #DOUBT
                    tempCode += "la $a0, STRING"+str(quad.arg1)+"\n"
                elif(type(quad.arg1)==type(1)):
                    tempCode += 'subu $sp, $sp, 4\n'
                    tempCode += 'li $t1,' + str(quad.arg1)+'\n'
                    tempCode += 'sw $t1, ($sp)\n'
                elif(type(quad.arg1)==type(1.0)):
                    tempCode += 'subu $sp, $sp, 4\n'
                    tempCode += 'li.s $f1,' + str(quad.arg1)+'\n'
                    tempCode += 's.s $f1, ($sp)\n'#can be a problem                
                
                elif("'" in quad.arg1):
                    tempCode += 'subu $sp, $sp, 4\n'
                
                    tempCode += 'li $t1, '+quad.arg1+'\n'
                    tempCode += 'sw $t1, ($sp)\n'
                else:
                    #assuming param is of type int
                    
                    
                    tempCode += 'subu $sp, $sp, 4\n'
                    
                    if(flag11==1):
                        tempCode += 'lw $t1, ' + str(arg1Location) + ' ($s0) \n'
                    else:
                        tempCode += 'lw $t1, _' + quad.arg1  + '\n'
                    
                    #tempCode += 'lw $t1, '+str(arg1Location)+'($s0)\n';
                    tempCode += 'sw $t1, ($sp)\n'
            elif(quad.op=='return'):
                if(type(quad.arg1)==type(1)):
                    tempCode += 'li $v0, '+str(quad.arg1)+'\n'
                elif(type(quad.arg1)==type(1.0)):
                    tempCode += 'li.s $f0, '+str(quad.arg1)+'\n'    
                    #tempCode += 'li $t1,' + str(quad.arg1)+'\n'
                    #tempCode += 'sw $t1, $s0\n'
                
                else:
                    if(debug5):
                        print "PRINTING FLAG11 !!! ", flag11
                    '''
                    if(funcReturnType):
                        reg = '$v0'
                    else:
                        reg = '$f0'
                    '''
                    if(flag11==1):
                        if(quad.opType!='REAL'):
                            tempCode += 'lw ' + '$v0'+ ', ' + str(arg1Location) + ' ($s0) \n'
                        else:
                            tempCode += 'l.s ' + '$f0'+ ', ' + str(arg1Location) + ' ($s0) \n'
                    else:
                        if(quad.opType!='REAL'):
                            tempCode += 'lw ' +  '$v0'+ ', _' + quad.arg1  + '\n'
                        else:
                            tempCode += 'l.s ' +  '$f0'+ ', _' + quad.arg1  + '\n'
                    
                    #tempCode += 'lw $v0, '+str(arg1Location)+'($s0)\n'
                
                
                assemblyOffset = funcFrameSize - instrSize          
                
                if(funcReturnType):
                    tempCode += "lw $ra, "+ str(assemblyOffset) +"($sp)\n"      #reload saved registers, and add sp, jump to return address
                    assemblyOffset -= instrSize
                tempCode += "lw $fp, "+ str(assemblyOffset) + "($sp)\n"
                assemblyOffset -= instrSize
                
                tempCode+="addu $sp, $sp, " + str(funcFrameSize) + "\n"
                tempCode += 'lw $s0, ($sp)\n'
                tempCode += 'addu $sp, $sp, 4\n'
                tempCode += "addu $sp, $sp, "+str(instrSize*len(funcEntry.type))+'\n'
                tempCode+="jr $ra\n"
                
            elif(quad.op=='call'):
                #DOUBT
                if(quad.arg1 == 'Out.Ln'):
                    tempCode += 'jal Ln\n'
                elif(quad.arg1 == 'Out.Int'):
                    #tempCode += 'move $a0, $t1\n'
                    tempCode += 'lw $a0, ($sp)\n';
                    tempCode += 'li $v0, 1\n'
                    tempCode += 'syscall\n'
                    tempCode += "la $a0, linespace\n"#by default print a line space
                    tempCode += "li $v0,4\n"
                    tempCode += "syscall\n"
                    tempCode += "addu $sp, $sp, 4\n"
                elif(quad.arg1 == 'Out.Char'):
                    #tempCode += 'move $a0, $t1\n'
                    tempCode += 'lw $a0, ($sp)\n';
                    tempCode += 'li $v0, 11\n'
                    tempCode += 'syscall\n'
                    tempCode += "la $a0, linespace\n"#by default print a line space
                    tempCode += "li $v0,4\n"
                    tempCode += "syscall\n"
                    tempCode += "addu $sp, $sp, 4\n"
                elif(quad.arg1 == 'Out.Real'):
                    #code+="\nl.s $f12,_day3 \nli $v0, 2\nsyscall\n";
                    #tempCode += 'mov.s $f12, $f1\n'
                    tempCode += 'l.s $f12, ($sp)\n';
                    tempCode += 'li $v0, 2\n'
                    tempCode += 'syscall\n'
                    tempCode += "la $a0, linespace\n"#by default print a line space
                    tempCode += "li $v0,4\n"
                    tempCode += "syscall\n"
                    tempCode += "addu $sp, $sp, 4\n"
                elif(quad.arg1 == 'Out.String'):
                    tempCode += "li $v0,4\n"
                    tempCode += "syscall\n"
                    tempCode += "la $a0, linespace\n"#by default print a line space
                    tempCode += "li $v0,4\n"
                    tempCode += "syscall\n"
                    #tempCode += "addu $sp, $sp, 4\n"
                else:    
                    tempCode += 'subu $sp, $sp, 4\n'
                    tempCode += 'sw $s0, ($sp)\n'
                    tempCode += 'jal '+quad.arg1+'\n'                 

                    
    elif(procname == ''):
        
        if(quad.op=='+'):
            if(quad.opType == 'INTEGER'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';   
                tempCode += 'add $t0,$t1,$t2 \n';
                tempCode += 'sw $t0,_'+quad.result+'\n';
            elif(quad.opType == 'REAL'):
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1.0)):
                    tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                tempCode += 'add.s $f0,$f1,$f2 \n';
                tempCode += 's.s $f0,_'+quad.result+'\n';        
                
        elif(quad.op=='-'):
            if(quad.opType == 'INTEGER'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';   
                tempCode += 'sub $t0,$t1,$t2 \n';
                tempCode += 'sw $t0,_'+quad.result+'\n';
            elif(quad.opType == 'REAL'):
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1.0)):
                    tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                tempCode += 'sub.s $f0,$f1,$f2 \n';
                tempCode += 's.s $f0,_'+quad.result+'\n';        
        elif(quad.op=='*'):
            if(quad.opType == 'INTEGER'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';   
                tempCode += 'mul $t0,$t1,$t2 \n';
                tempCode += 'sw $t0,_'+quad.result+'\n';
            elif(quad.opType == 'REAL'):
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1.0)):
                    tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                tempCode += 'mul.s $f0,$f1,$f2 \n';
                tempCode += 's.s $f0,_'+quad.result+'\n';                 
        elif(quad.op=='DIV'):
            if(quad.opType == 'INTEGER'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';   
                tempCode += 'div $t1,$t2 \n';
                tempCode += 'mflo $t0\n';
                tempCode += 'sw $t0,_'+quad.result+'\n';
                  
        elif(quad.op=='MOD'):
            if(quad.opType == 'INTEGER'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';   
                tempCode += 'div $t1,$t2 \n';
                tempCode += 'mfhi $t0\n';
                tempCode += 'sw $t0,_'+quad.result+'\n';
        elif(quad.op=='/'):
            if(quad.opType == 'REAL'):
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1.0)):
                    tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'l.s $f2, _'+quad.arg2+'\n';   
                tempCode += 'div.s $f0,$f1,$f2 \n';
                tempCode += 's.s $f0,_'+quad.result+'\n';            
        elif(quad.op in relOps):
            if(debug5):
                print "Entered relOps", quad.Print(-1)
            if(quad.opType=='INTEGER'):
                if(debug5):
                    print "Entered integer relOps"
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1)):
                    tempCode += 'li $t2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'lw $t2, _'+quad.arg2+'\n';
                if(quad.op=='<'):
                    tempCode += 'blt $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.op=='<='):
                    tempCode += 'ble $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.op=='>'):
                    tempCode += 'bgt $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.op=='>='):
                    tempCode += 'bge $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.op=='='):
                    tempCode += 'beq $t1, $t2, _'+str(quad.result)+'\n'
                elif(quad.op=='#'):
                    tempCode += 'bne $t1, $t2, _'+str(quad.result)+'\n'
            elif(quad.opType=='REAL'):
                if(debug5):
                    print "Entered real relOps"
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(type(quad.arg2) == type(1.0)):
                    tempCode += 'li.s $f2,'+str(quad.arg2)+'\n';
                else:
                    tempCode += 'l.s $f2, _'+quad.arg2+'\n';
                if(quad.op=='<'):
                    tempCode += 'c.lt.s $f1, $f2 \n'
                    tempCode += 'bc1t _'+str(quad.result)+'\n';
                elif(quad.op=='<='):
                    tempCode += 'c.le.s $f1, $f2 \n'
                    tempCode += 'bc1t _'+str(quad.result)+'\n';
                elif(quad.op=='>'):
                    tempCode += 'c.le.s $f1, $f2 \n'
                    tempCode += 'bc1f _'+str(quad.result)+'\n';
                elif(quad.op=='>='):
                    tempCode += 'c.lt.s $f1, $f2 \n'
                    tempCode += 'bc1f _'+str(quad.result)+'\n';
                elif(quad.op=='='):
                    tempCode += 'c.eq.s $f1, $f2 \n';
                    tempCode += 'bc1t _'+str(quad.result)+'\n'
                elif(quad.op=='#'):
                    tempCode += 'c.eq.s $f1, $f2 \n';
                    tempCode += 'bc1f _'+str(quad.result)+'\n'             
        elif(quad.op in unaryOps):
            if(debug5):
                print "Entered unaryOps", quad.Print(-1)
            if(quad.op == 'intToReal'):
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n';
                tempCode += 'mtc1 $t1, $f0 \n';
                tempCode += 'cvt.s.w $f0, $f0\n';    
                tempCode += 's.s $f0,_'+quad.result+'\n';   
            elif(quad.opType=='INTEGER'):
                if(debug5):
                    print "Entered integer unaryOps"
                if(type(quad.arg1) == type(1)):
                    tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'lw $t1, _'+quad.arg1+'\n';
                if(quad.op=='UMINUS'):
                     tempCode += 'neg $t0, $t1\n'
                     tempCode += 'sw $t0,_'+quad.result+'\n';
                elif(quad.op=='UPLUS'):
                     tempCode += 'sw $t1,_'+quad.result+'\n';
            elif(quad.opType=='REAL'):
                if(debug5):
                    print "Entered real unaryOps";
                if(type(quad.arg1) == type(1.0)):
                    tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                else:
                    tempCode += 'l.s $f1, _'+quad.arg1+'\n'; 
                if(quad.op=='UMINUS'):
                     tempCode += 'neg.s $f0, $f1\n'
                     tempCode += 's.s $f0,_'+quad.result+'\n';
                elif(quad.op=='UPLUS'):
                     tempCode += 's.s $f1,_'+quad.result+'\n';
        elif(quad.op=='goto'):
            tempCode += 'b _'+str(quad.result)+'\n'
        elif(quad.op=='ifgoto'):
            tempCode += 'lw $t0, _'+quad.arg1+'\n'
            tempCode += 'beq $t0,1, _'+str(quad.result)+'\n'
        elif(quad.op == 'READINT'):
            tempCode += 'li $v0 , 5\n';
            tempCode += 'syscall\n';
            tempCode += 'sw $v0, _'+str(quad.arg1)+'\n';
        elif(quad.op == 'READREAL'):
            tempCode += 'li $v0 , 6\n';
            tempCode += 'syscall\n';
            tempCode += 's.s $f0, _'+str(quad.arg1)+'\n';            
        elif(quad.op is None):
            if(quad.arg1=='retval'):
                #tempCode += 'addu $sp, $sp, 4\n'
                if(funcReturnType=='INTEGER'):
                    reg = '$v0'
                else:
                    reg = '$f0'
                
                if(funcReturnType=='INTEGER'):
                    tempCode += 'sw $v0, _'+quad.result+'\n'
                else:
                    tempCode += 's.s $f0, _'+quad.result+'\n'
                
                
            elif(type(quad.arg1) == type(1)):
                tempCode += 'li $t1,'+str(quad.arg1)+'\n';
                if('(' in quad.result):
                     split1 = quad.result.split('(')
                     place = split1[1].split(')')[0]
                     tempCode += 'lw $t0, _'+place+'\n';
                     tempCode += 'la $t3, _'+firstSymbol+'\n'
                     tempCode += 'add $t0, $t0, $t3\n'
                     tempCode += 'sw $t1,($t0)\n';
                else: 
                     tempCode += 'sw $t1,_'+quad.result+'\n';

                #tempCode += 'sw $t1,_'+quad.result+'\n';
            elif(type(quad.arg1) == type(1.0)):
                tempCode += 'li.s $f1,'+str(quad.arg1)+'\n';
                
                
                if('(' in quad.result):
                     split1 = quad.result.split('(')
                     place = split1[1].split(')')[0]
                     tempCode += 'lw $t0, _'+place+'\n';
                     tempCode += 'la $t3, _'+firstSymbol+'\n'
                     tempCode += 'add $t0, $t0, $t3\n'
                     tempCode += 's.s $f1,($t0)\n';
                else: 
                     tempCode += 's.s $f1,_'+quad.result+'\n';
                    
                
                #tempCode += 's.s $f1,_'+quad.result+'\n';
            elif(quad.arg1==True):
                tempCode += 'li $t1, 1\n';
                tempCode += 'sw $t1,_'+quad.result+'\n';
            elif(quad.arg1==False):
                tempCode += 'li $t1, 0\n';
                tempCode += 'sw $t1,_'+quad.result+'\n';
            elif(quad.opType == 'CHAR'):
                tempCode += 'li $t1,' + quad.arg1+'\n';
                tempCode += 'sw $t1,_'+quad.result+'\n';
            else:
                isReal = False;
                global stack;
                symbolTable = stack[len(stack)-1]
                if('(' in quad.arg1):
                    relEntry = symbolTable.LookUp(quad.result)
                    if(relEntry.type=='REAL'):
                        isReal = True
                else:
                    relEntry = symbolTable.LookUp(quad.arg1)
                    if(relEntry.type=='REAL'):
                        isReal = True
                #if(quad.arg1)
                # type of arg1 should be lookedup and the flag set accordingly
                if('(' in quad.arg1):
                    #print "entered rvalue"
                    split1 = quad.arg1.split('(')
                    place = split1[1].split(')')[0]
                    if(split1[0]=='rValue'):
                        tempCode += 'lw $t1, _'+place+'\n';
                        tempCode += 'la $t3, _'+firstSymbol+'\n'
                        tempCode += 'add $t1, $t1, $t3\n'
                        if(isReal):
                            tempCode += 'l.s $f1, ($t1)\n';
                        else:
                            tempCode += 'lw $t1, ($t1)\n'; 
                    else:
                        tempCode += 'la $t1, _'+place+'\n'; 
                else:
                    if(isReal):
                            tempCode += 'l.s $f1, _'+quad.arg1+'\n';
                    else:
                            tempCode += 'lw $t1, _'+quad.arg1+'\n';
                    #tempCode += 'lw $t1, _'+quad.arg1+'\n';
                
                #print "printing xyz", quad.result
                if('(' in quad.result):
                    #print "entered lvalue"
                    split1 = quad.result.split('(')
                    place = split1[1].split(')')[0]
                    tempCode += 'lw $t0, _'+place+'\n';
                    tempCode += 'la $t3, _'+firstSymbol+'\n'
                    tempCode += 'add $t0, $t0, $t3\n'
                    if(isReal):
                            tempCode += 's.s $f1,($t0)\n';
                    else:
                            tempCode += 'sw $t1,($t0)\n';
                    #tempCode += 'sw $t1,($t0)\n';
                else:
                    if(isReal):
                            tempCode += 's.s $f1,_'+quad.result+'\n';
                    else:
                            tempCode += 'sw $t1,_'+quad.result+'\n';
                    #tempCode += 'sw $t1,_'+quad.result+'\n';
            
                
                
                
                
                
                
                
                
                
                
                
                #print "op is none..what to do??", quad.arg1, type(quad.arg1), quad.opType;
                #tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                #tempCode += 'sw $t1,_'+quad.result+'\n';
        elif(quad.op=='param'):
            if(quad.opType == 'STRING'):
                #DOUBT
                tempCode += "la $a0, STRING"+str(quad.arg1)+"\n"
            elif(type(quad.arg1)==type(1)):
                tempCode += 'subu $sp, $sp, 4\n'
                tempCode += 'li $t1,' + str(quad.arg1)+'\n'
                tempCode += 'sw $t1, ($sp)\n'
            elif(type(quad.arg1)==type(1.0)):
                tempCode += 'subu $sp, $sp, 4\n'
                tempCode += 'li.s $f1,' + str(quad.arg1)+'\n'
                tempCode += 's.s $f1, ($sp)\n'#can be a problem                
            elif("'" in quad.arg1):
                tempCode += 'subu $sp, $sp, 4\n'
            
                tempCode += 'li $t1, '+quad.arg1+'\n'
                tempCode += 'sw $t1, ($sp)\n'

            else:
                tempCode += 'subu $sp, $sp, 4\n'
                tempCode += 'lw $t1, _'+quad.arg1+'\n'; 
                tempCode += 'sw $t1, ($sp)\n'
            
                
                
        elif(quad.op=='call'):
            #DOUBT
            if(quad.arg1 == 'Out.Ln'):
                tempCode += 'jal Ln\n'
            elif(quad.arg1 == 'Out.Int'):
                #tempCode += 'move $a0, $t1\n'
                tempCode += 'lw $a0, ($sp)\n';
                tempCode += 'li $v0, 1\n'
                tempCode += 'syscall\n'
                tempCode += "la $a0, linespace\n"#by default print a line space
                tempCode += "li $v0,4\n"
                tempCode += "syscall\n"
                tempCode += "addu $sp, $sp, 4\n"
            elif(quad.arg1 == 'Out.Char'):
                #tempCode += 'move $a0, $t1\n'
                tempCode += 'lw $a0, ($sp)\n';
                tempCode += 'li $v0, 11\n'
                tempCode += 'syscall\n'
                tempCode += "la $a0, linespace\n"#by default print a line space
                tempCode += "li $v0,4\n"
                tempCode += "syscall\n"
                tempCode += "addu $sp, $sp, 4\n"
            elif(quad.arg1 == 'Out.Real'):
                #code+="\nl.s $f12,_day3 \nli $v0, 2\nsyscall\n";
                #tempCode += 'mov.s $f12, $f1\n'
                tempCode += 'l.s $f12, ($sp)\n';
                tempCode += 'li $v0, 2\n'
                tempCode += 'syscall\n'
                tempCode += "la $a0, linespace\n"#by default print a line space
                tempCode += "li $v0,4\n"
                tempCode += "syscall\n"
                tempCode += "addu $sp, $sp, 4\n"
            elif(quad.arg1 == 'Out.String'):
                tempCode += "li $v0,4\n"
                tempCode += "syscall\n"
                tempCode += "la $a0, linespace\n"#by default print a line space
                tempCode += "li $v0,4\n"
                tempCode += "syscall\n"
                #tempCode += "addu $sp, $sp, 4\n"
            else:    
                tempCode += 'subu $sp, $sp, 4\n'
                tempCode += 'sw $s0, ($sp)\n'
                tempCode += 'jal '+quad.arg1+'\n' 
    return tempCode
            
#            if(table):
#            table.Print()
#        else:
#            print "function not found"

def sort(tableList):
    global firstSymbol;
    i = 0
    j = 0 
    var = VarEntry()
    array = ArrayEntry()
    for i in range(0, len(tableList)-1):
        j=0
        for j in range(i+1, len(tableList)):
            if((type(tableList[i][1])==type(var) or type(tableList[i][1])==type(array)) and (type(tableList[j][1])==type(var) or type(tableList[j][1])==type(array))):
                if(tableList[j][1].offset < tableList[i][1].offset):
                    temp = tableList[i]
                    tableList[i] = tableList[j]         #check for assignment stuff of python
                    tableList[j] = temp
            j+=1
        i+=1
    firstSymbol = tableList[0][0]
funcNo = 0

code += genBy;
code += ".data\n";

#code+="_globalVariables: \n"

var = VarEntry()
arr = ArrayEntry()
tableList = symbolTable.symbolDictionary.items()

sort(tableList)             #sort it with respect to the offset

for (id, entry) in tableList:                 #set up space for global variables
    #entry = symbolTable.symbolDictionary[id]
    if(type(var)==type(entry)):
        if(entry.type=='INTEGER'):
            code+="_"+id+":\n";
            code+=".space "+str(intSize)+"\n"
            #code+=str(entry.offset)+"\n"
        elif(entry.type=='REAL'):
            code+="_"+id+":\n";
            code+=".space "+str(realSize)+"\n"
        elif(entry.type=='BOOLEAN'):
            code+="_"+id+":\n";
            code+=".space "+str(booleanSize)+"\n"
            #code+=str(entry.offset)+"\n"
        elif(entry.type=='CHAR'):
            code+="_"+id+":\n";
            code+=".space "+str(charSize)+"\n"
    elif(type(arr)==type(entry)):
        if(debug5):
            print "found array"
            print entry.type;
        if(entry.type['type']=='INTEGER'):
            if(debug5):
                print "found integer array"
            code+="_"+id+":\n";
            code+=".space "+str(entry.length*intSize)+"\n"
                
#now, you'll be able to access global variables of offset t using _globalVariables(t)
code+="\nlinespace:\n .asciiz \" \\n\"\n\n";

num = 1;
for ele in stringList:
    code+="\nSTRING"+str(num)+":\n .asciiz "+str(ele)+"\n";
    num += 1;

code+="\n.text\n";   
def initialize():
    global code,tableList,var
    code+="main:\n" 
    code += "li $t0,0\n";
    for (id, entry) in tableList:                #assigning them 0 by default
        #entry = symbolTable.symbolDictionary[id]
        if(type(var)==type(entry)):
            if(entry.type=='INTEGER'):
                code+="sw $t0,_"+id+"\n";
            elif(entry.type=='REAL'):
                code+="sw $t0,_"+id+"\n"; # would be changed!
                
                

# STRENGTH REDUCTION
def optimize(quad):
    if(quad.op == '+'):
        if(quad.arg1 == 0):
            quad.op = None;
            quad.arg1 = quad.arg2;
            quad.arg2 = None;
        if(quad.arg2 == 0):
            quad.op = None; 
    elif(quad.op == '*'):
        if(quad.arg1 == 0):
            quad.op = None;
        elif(quad.arg1 == 1):
            quad.op = None;
            quad.arg1 = quad.arg2;
            quad.arg2 = None;            
        if(quad.arg2 == 0):
            quad.op = None;   
            quad.arg1 = 0;
        elif(quad.arg2 == 1):
            quad.op = None;
    elif(quad.op == 'DIV'):
        if(quad.arg2 == 1):
            quad.op = None;  
    elif(quad.op == 'MOD'):
        if(quad.arg2 == 1):
            quad.op = None;
            quad.arg1 = 0;  
        
label=0;        



for quad in quadList:
    optimize(quad);
    tempCode = '';
    #if(label in targetList):
    tempCode+= "_"+str(label)+":\n";
    label=label+1;
    
    '''if(quad.op == 'BEGIN_FUNC'):
        funcStack.append(quad.arg1)
        #print funcStack
       ''' 
       
    if(quad.op=='BEGINMAIN'):
        initialize()
    
    if(quad.op=='ENDMAIN' or quad.op == 'EXIT'):
        code += 'jal halt\n'
    
    elif(len(funcStack) != 0):                #i.e.,a function quad            
        tempCode += translate(quad, funcStack[len(funcStack)-1][0], label)
        
    else:                           #i.e., a global quad
        tempCode  += translate(quad, '', label)
    
    '''if(quad.op == 'END_FUNC'):
        funcStack.pop()
        #print funcStack
        
    '''
    
    '''if(len(funcStack) != 0):                #i.e.,a function quad            
        translateQuad(quad, funcStack[len(funcStack)-1], label)
        
    else:                           #i.e., a global quad
        translateQuad(quad, '', label)
    '''
    
        
    if(tempCode is not None):
        code += tempCode
        
"""
code+= "_"+str(label)+":\n";
newLinePrintingCode = "\njal Ln\n"
code+= newLinePrintingCode;\
code+="\nlw $a0,_day2 \nli $v0, 1\nsyscall\n";
code+= newLinePrintingCode;
#l.s     $f12,val        # use the float as an argument
#li      $v0,2           # code 2 == print float
#        syscall
code+="\nl.s $f12,_day3 \nli $v0, 2\nsyscall\n";
code+= newLinePrintingCode;
"""
def defaultPrinting():
    global code;
    # printing day2 and day3
    newLinePrintingCode = "\njal Ln\n"
    code+= newLinePrintingCode;
    code+="\nlw $a0,_day2 \nli $v0, 1\nsyscall\n";
    code+= newLinePrintingCode;
    code+="\nl.s $f12,_day3 \nli $v0, 2\nsyscall\n";
    code+= newLinePrintingCode;    

def endProgramMeasures():
    global code;
    code += "\nhalt:\n"
    #defaultPrinting();
    # main halt function
    code += "\nli $v0, 10\nsyscall\n" ;
    # linespace printing function
    code += "\nLn:\nla $a0, linespace\nli $v0,4\nsyscall\njr $ra"; 

endProgramMeasures()              
#print "assembly code : \n", code



f = open('new.asm', 'w');
f.write(code);

                       
