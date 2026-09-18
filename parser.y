%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void yyerror(const char *s);
int yylex(void);

extern FILE *yyin;
extern int yylineno;

int speed_limit = 0;

typedef struct
{
    char name[50];
    int speed;

} Vehicle;

Vehicle vehicles[100];

int vehicle_count = 0;


void add_vehicle(char *name, int speed)
{
    strcpy(
        vehicles[vehicle_count].name,
        name
    );

    vehicles[vehicle_count].speed = speed;

    vehicle_count++;
}


void analyze_traffic()
{
    int i;

    printf("\n");
    printf("========================================\n");
    printf(" SMART TRAFFIC VIOLATION ANALYZER\n");
    printf("========================================\n");

    printf(
        "Speed Limit: %d km/h\n\n",
        speed_limit
    );


    for(i = 0; i < vehicle_count; i++)
    {
        printf(
            "Vehicle: %s\n",
            vehicles[i].name
        );

        printf(
            "Speed: %d km/h\n",
            vehicles[i].speed
        );


        if(vehicles[i].speed > speed_limit)
        {
            printf(
                "Status: SPEED VIOLATION\n"
            );
        }

        else
        {
            printf(
                "Status: SAFE\n"
            );
        }


        printf(
            "----------------------------------------\n"
        );
    }
}

%}


%union
{
    int num;
    char *str;
}


%token LIMIT
%token VEHICLE
%token SPEED
%token ANALYZE

%token <num> NUMBER
%token <str> ID


%%


program:
      limit_statement vehicle_list analyze_statement
      {
          printf(
              "\nParsing Successful\n"
          );
      }
      ;


limit_statement:
      LIMIT NUMBER ';'
      {
          speed_limit = $2;

          printf(
              "Speed Limit Set: %d\n",
              speed_limit
          );
      }
      ;


vehicle_list:
      /* empty */

      |

      vehicle_list vehicle_statement
      ;


vehicle_statement:
      VEHICLE ID SPEED NUMBER ';'
      {
          add_vehicle(
              $2,
              $4
          );

          printf(
              "Vehicle Added: %s\n",
              $2
          );

          free($2);
      }
      ;


analyze_statement:
      ANALYZE ';'
      {
          analyze_traffic();
      }
      ;


%%


void yyerror(const char *s)
{
    printf(
        "Syntax Error at line %d: %s\n",
        yylineno,
        s
    );
}


int main(int argc, char *argv[])
{
    if(argc != 2)
    {
        printf(
            "Usage: %s input.txt\n",
            argv[0]
        );

        return 1;
    }


    yyin = fopen(
        argv[1],
        "r"
    );


    if(yyin == NULL)
    {
        printf(
            "Input File Open Error\n"
        );

        return 1;
    }


    yyparse();


    fclose(yyin);


    return 0;
}