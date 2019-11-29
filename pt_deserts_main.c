#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <Python.h>











// Decision: in order to avoid running into requirements problems, 
// make the main program in Python (bright side I get to learn more about Python I/O












/*  to-do:
      - handle errors that result from not giving enough parameters for a command (currently just hangs in a terrible way)
*/


int main(int argc, char *argv[]){  

  int echo = 0;
  if(argc > 1 && strcmp("-echo", argv[1]) == 0){
      echo = 1;
  }

  printf("\nPublic Transit Deserts by Jake Holicky\n");
  printf("github.com/jholicky/public_transit_deserts\n\n");
  printf("Commands:\n");
  printf("  ~ cache <area name> <north> <south> <east> <west>\n");
  printf("                            : saves an area named area name with given coordinates\n");
  printf("  ~ testcache <area name> <north> <south> <east> <west> <testHeight> <testWidth>\n");
  printf("                            : saves an area named area name with given coordinates \n");
  printf("                              and optional grid testHeight and testWidth\n");
  printf("  ~ iscached <area name>    : checks if the user has cached a given area name\n");
  printf("  ~ ptdeserts <area name>   : uses a cached area to find the most isolated grid point(s) from public transit\n");
  printf("  ~ summary                 : prints a summary of all cache files created\n");
  printf("  ~ info <area name>        : gives information on a cached file if it exists\n");
  printf("  ~ quit                    : quits the program\n\n");
  
  char cmd[128];
  int success;
  
  while(1){
    printf("PTD> ");
    success = fscanf(stdin,"%s",cmd);
        
    if(success == EOF){
      printf("\n");
      break;
    }
    
    if(strcmp("cache", cmd) == 0){ // not working for fewer than 7 parameters (not counting the command cache)
      int i = 0;
      int numParams = 5;
      char params[128][numParams];
      while(1){
        success = fscanf(stdin, "%s", params[i]);
        if(success == EOF){
          break;
        }
        i++;
        if(i >= numParams){
          break;
        }
      }
      if(echo){
        int j = 0;
        while(j <= i){
          printf("%s", params[i]);
          j++;
        }
        printf("\n");
      }
      // do cache
    }
      
    if(strcmp("testcache", cmd) == 0){ // not working for fewer than 7 parameters (not counting the command cache)
      int i = 0;
      int numParams = 7;
      char params[128][numParams];
      while(1){
        success = fscanf(stdin, "%s", params[i]);
        if(success == EOF){
          break;
        }
        i++;
        if(i >= numParams){
          break;
        }
      }
      if(echo){
        int j = 0;
        while(j <= i){
          printf("%s", params[i]);
          j++;
        }
        printf("\n");
      }
      // do testcache
    }
    
    if(strcmp("iscached", cmd) == 0){
      char params[128][2];
      if(fscanf(stdin, "%s", params[0]) == EOF){
        printf("not enough parameters\n");
        break;
      }
      
      if(echo){
        printf("iscached %s\n", params[0]);
      }
      
      char pycode[128];
      char *pycode1 = "from pt_desert_funcs import cached";
      char *pycode2 = "print(cached(";
      char *pycode4 = "))";
      /*
      strcpy(pycode, "python -c ");
      strcat(pycode, pycode1);
      system(pycode);
      
      strcpy(pycode, "python -c ");
      strcat(pycode, pycode2);
      strcat(pycode, params[0]);
      strcat(pycode, pycode4);
      system(pycode);
      */
      //strcpy(pycode, "python -c print('hello\n')");
      //strcpy(pycode, "ls -l");
      //system(pycode);
      
      PyObject* pInt;

	    Py_Initialize();

	    PyRun_SimpleString("print('Hello World from Embedded Python!!!')");
	    
	    Py_Finalize();
    }
    
    if(strcmp("ptdeserts", cmd) == 0){
      char params[128][2];
      if(fscanf(stdin, "%s", params[0]) == EOF){
        printf("not enough parameters\n");
        break;
      }
      
      if(echo){
        printf("ptdeserts %s\n", params[0]);
      }
      
      // do ptdeserts
    }
    
    if(strcmp("summary", cmd) == 0){
      char params[128];
      if(echo){
        printf("summary\n");
      }
      
      // do summary
    }
    
    if(strcmp("info", cmd) == 0){
      char params[128][2];
      if(fscanf(stdin, "%s", params[0]) == EOF){
        printf("not enough parameters\n");
        break;
      }
      
      if(echo){
        printf("info %s\n", params[0]);
      }
      
      // do info
    }
    
    if (strcmp("quit", cmd) == 0){
      char params[128];
      if(echo){
        printf("quit\n");
      }
      break;
    }   
  }
  
  return 0; 
}
