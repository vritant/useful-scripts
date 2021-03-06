alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

alias gitaddmodified='git status | grep modified | cut --complement -c1-14 | xargs git add'
alias gitrmdeleted='git status | grep deleted | cut --complement -c1-14 | xargs git rm'
alias gitresetmodified='git status | grep modified | cut --complement -c1-14 | xargs git checkout -- '
alias gitaddnewfiles='git ls-files --others --exclude-standard | xargs git add'
alias gitimpfiles='git status | grep -v ucd | grep -v uml | grep -v jpg | grep -v todo'
alias rmtilde='find -name "*~" | xargs rm'
alias fileschanged='git status | grep modified | cut --complement -c1-14'
alias mark='location=`pwd`'
alias go2mark='cd $location'
alias mci='mvn clean install'
alias rmdiff='find -name diff.txt | xargs rm'
alias go2gitrepos='cd /home/vritant/gitRepos'
export PS1='[\u@\h \W$(__git_ps1 " (%s)")]\$ '

alias savecommand='history | tail -n 2 | head -n 1 | cut --complement -c1-7 | cat >> ~/favcommands.fav'
alias lookupcommand='cat ~/favcommands.fav | grep'
runcommandfunction() {
lookupcommand $1 | head -$2 | tail -n 1 | xargs -0 bash -c
}
alias runcommand=runcommandfunction

