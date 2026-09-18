%{
#include "parser.tab.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
%}

%option noyywrap
%option yylineno

%%

"LIMIT"                 { return LIMIT; }
"VEHICLE"               { return VEHICLE; }
"SPEED"                 { return SPEED; }
"ANALYZE"               { return ANALYZE; }

[0-9]+                  {
                            yylval.num = atoi(yytext);
                            return NUMBER;
                        }

[a-zA-Z_][a-zA-Z0-9_]*  {
                            yylval.str = malloc(strlen(yytext) + 1);
                            strcpy(yylval.str, yytext);
                            return ID;
                        }

";"                     { return ';'; }

[ \t\r\n]+              { }

.                       {
                            printf(
                                "Lexical Error at line %d: %s\n",
                                yylineno,
                                yytext
                            );
                        }

%%