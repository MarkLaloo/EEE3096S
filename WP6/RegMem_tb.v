`timescale 1ns / 1ps

module tb_reg_mem;

    parameter DATA_WIDTH = 8; //8 bit wide data
    parameter ADDR_BITS = 5; //32 Addresses

    reg [ADDR_BITS-1:0] addr;
    reg [DATA_WIDTH-1:0] data_in;
    wire [DATA_WIDTH-1:0] data_out;
    reg wen, clk;

    //Note passing of parameters syntax
    reg_mem #(DATA_WIDTH,ADDR_BITS) RM (addr, data_in, wen, clk, data_out);

    initial begin
        // For use in EDAPlayground
        $dumpfile("dump.vcd");
        $dumpvars(1, tb_reg_mem);
        
        
        clk = 0;
        wen = 1;
       
        //Write to 31 addresses 
        for(int i=0;i<32;i=i+1) // write from 0 and increase by 1 till 31 
        begin
            data_in = i; 
            addr = (i); // not incrementing address by 2
            $display("Write %d to address %d",data_in,addr);
            repeat (2) #1 clk = ~clk;
        end
        wen =0;
        #1;
        //Read from 31 addresses 
        for(int i=0;i<32;i=i+1) // read from 0 and increase by 1 till 31
        begin
            data_in = i; 
            addr = (i);// not incrementing address by 2
            $display("Read %d from address %d",data_in,addr);
            repeat (2) #1 clk = ~clk;
        end


        
    end
endmodule