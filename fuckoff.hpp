// fuckoff.hpp - single header anti debug
// - prevents ptrace
// - prevents core dumps
// CAN BE EASILY PATCHED, this is meant to be used in combination with udf2s

#include <unistd.h>
#include <stdlib.h>
#include <sched.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <sys/ptrace.h>

void __attribute__((constructor)) start_trace() {
    prctl(PR_SET_DUMPABLE, 0);
    int f_pid = fork();

    if (f_pid == 0) {
        prctl(PR_SET_DUMPABLE, 0);
        int err = ptrace(PTRACE_ATTACH, getppid(), NULL, NULL);
        waitpid(getppid(), NULL, 0);

        if (err != 0) {
            kill(getppid(), SIGKILL);
            exit(0);
        }

        ptrace(PTRACE_SETOPTIONS, getppid(), NULL, PTRACE_O_EXITKILL);
        ptrace(PTRACE_CONT, getppid(), NULL);

        while (1) {
            sched_yield();
        }
    } else {
        int err = ptrace(PTRACE_ATTACH, f_pid, NULL, NULL);
        waitpid(f_pid, NULL, 0);

        if (err != 0) {
            kill(f_pid, SIGKILL);
            exit(0);
        }

        ptrace(PTRACE_SETOPTIONS, f_pid, NULL, PTRACE_O_EXITKILL);
        ptrace(PTRACE_CONT, f_pid, NULL);
    }
}
