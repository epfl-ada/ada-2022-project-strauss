// Logic to compute Pagerank of a huge matrix using Petsc. Do not run unless the machine has more than 220GB of RAM.
// Preprocesing logic is single-threaded, but pagerank computing is multithreaded.
// This can't be built without our Makefile, Petsc example makefile can be utilized to build this.

#include<petsc.h>
#include<petscmat.h>
#include<petsctime.h>
#include<petscsys.h>
#include<limits>

PetscInt N = 136470;
int main_thread_rank = 0;
int self_rank, proc_size;
PetscInt local_row_size;

PetscErrorCode output_matrix(Mat *X, const char* file_name) {
    const PetscReal *cache;
    int fd;
    PetscFunctionBeginUser;
    PetscCall(PetscBinaryOpen(file_name, FILE_MODE_WRITE, &fd));
    for(int i = 0; i < N; i++) {
      PetscCall(MatGetRow(*X, i, NULL, NULL, &cache));
      PetscCall(PetscBinaryWrite(fd, cache, N, PETSC_REAL));
      PetscCall(MatRestoreRow(*X, i, NULL, NULL, &cache));
      PetscCall(PetscPrintf(PETSC_COMM_SELF, "%f - %s output done! \n", (1.0*i)/N, file_name));
    }
    PetscCall(PetscBinaryClose(fd));
    PetscFunctionReturn(0);
}

PetscErrorCode read_matrix(Mat *X, const char* file_name) {
    const PetscReal *cache;
    int fd;
    PetscInt l_start, l_end;
    PetscInt cols[N];
    PetscInt rows[2*N];
    off_t offf;
    PetscReal buffer[N*5];
    PetscFunctionBeginUser;
    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "Begin reading the matrix! \n"));
    PetscCall(MatCreateDense(PETSC_COMM_WORLD, local_row_size, N, N, N, NULL, X));
    PetscCall(PetscBinaryOpen(file_name, FILE_MODE_READ, &fd));
    PetscCall(MatGetOwnershipRange(*X, &l_start, &l_end));
    PetscCall(PetscBinarySeek(fd, PETSC_BINARY_SCALAR_SIZE*N*l_start, PETSC_BINARY_SEEK_SET, &offf));
    for(int i = 0; i < (l_end-l_start); i++) rows[i] = i;
    for(int i = 0; i < N; i++) cols[i] = i;

    for(int i = l_start; i < l_end; i+=5) {
        PetscInt write_count = (i < (l_end-5)) ? 5 : (l_end - i) - 1;
        PetscCall(PetscBinaryRead(fd, buffer, N*write_count, NULL, PETSC_REAL));
        PetscCall(MatSetValuesLocal(*X, write_count, &rows[i-l_start], N, cols, buffer, INSERT_VALUES));
        MatAssemblyBegin(*X, MAT_FLUSH_ASSEMBLY);
        MatAssemblyEnd(*X, MAT_FLUSH_ASSEMBLY);
        PetscCall(PetscPrintf(PETSC_COMM_WORLD, "%f - %s - done! \n", (1.0*i)/(l_end-l_start), file_name));

    }
    PetscCall(PetscBinaryClose(fd));
    MatAssemblyBegin(*X, MAT_FINAL_ASSEMBLY);
    MatAssemblyEnd(*X, MAT_FINAL_ASSEMBLY);

    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "End reading the matrix! \n"));
    PetscFunctionReturn(0);
}

// This completed the matrix exported by previous steps (basically non-normalized weight matrix)
PetscErrorCode create_graph_mat(Mat *graph_mat) {
    char file_A_partial[128];
    PetscViewer viewer;
    Mat graph_mat_T;
    PetscFunctionBeginUser;
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "Graph matrix Load - Begin.\n"));

    PetscCall(PetscOptionsGetString(NULL, NULL, "-graph_mat_partial", file_A_partial, sizeof(file_A_partial), NULL));
    PetscCall(MatCreateDense(PETSC_COMM_SELF, PETSC_DECIDE, PETSC_DECIDE, N, N, NULL, graph_mat));

    int fd;
    PetscReal cached_vals[N];
    PetscInt cols[N];
    for(int i = 0; i < N; i++) cols[i] = i;
    off_t off;
    PetscCall(PetscBinaryOpen(file_A_partial, FILE_MODE_READ, &fd));
    for(int i = 0; i < N; i++) {
        PetscInt row_loc[1];
        row_loc[0] = i;

        PetscCall(PetscBinaryRead(fd, cached_vals, N-i-1, NULL, PETSC_REAL));
        PetscCall(MatSetValues(*graph_mat, 1, row_loc, N-i-1, &cols[i+1], cached_vals, INSERT_VALUES));
        PetscCall(PetscPrintf(PETSC_COMM_SELF, "%f - graph_mat - done! \n", (1.0*i)/N));
    }
    PetscCall(PetscBinaryClose(fd));
    MatAssemblyBegin(*graph_mat, MAT_FINAL_ASSEMBLY);
    MatAssemblyEnd(*graph_mat, MAT_FINAL_ASSEMBLY);

    PetscCall(MatTranspose(*graph_mat, MAT_INITIAL_MATRIX, &graph_mat_T));
    PetscCall(MatAXPY(*graph_mat, 1.0, graph_mat_T, UNKNOWN_NONZERO_PATTERN));
    PetscCall(MatDestroy(&graph_mat_T));
    PetscCall(output_matrix(graph_mat, "graph.mat"));

    PetscCall(PetscPrintf(PETSC_COMM_SELF, "Graph matrix Load - Done. \n"));
    PetscFunctionReturn(0);
}

// aux_data should be allocated with N spaces
PetscErrorCode read_aux_file(PetscReal *aux_data) {
    int fd;
    char file_aux[128];
    PetscFunctionBeginUser;
    PetscCall(PetscOptionsGetString(NULL, NULL, "-aux", file_aux, sizeof(file_aux), NULL));
    PetscCall(PetscBinaryOpen(file_aux, FILE_MODE_READ, &fd));
    PetscCall(PetscBinaryRead(fd, aux_data, N, NULL, PETSC_REAL));
    PetscCall(PetscBinaryClose(fd));
    PetscFunctionReturn(0);
}

PetscErrorCode write_matrix_view(Mat *X, const char * file_name) {
    PetscViewer viewer;
    PetscFunctionBeginUser;
    PetscCall(PetscViewerBinaryOpen(PETSC_COMM_WORLD, file_name, FILE_MODE_WRITE, &viewer));
    PetscCall(MatView(*X, viewer));
    PetscCall(PetscViewerDestroy(&viewer));
    PetscFunctionReturn(0);
}

PetscErrorCode read_matrix_view(Mat *X, const char * file_name) {
    PetscViewer viewer;
    PetscFunctionBeginUser;
    PetscCall(MatCreateAIJ(PETSC_COMM_WORLD, local_row_size, N, N, N, PETSC_DEFAULT, NULL, PETSC_DEFAULT, NULL, X));
    PetscCall(MatSetOption(*X, MAT_IGNORE_ZERO_ENTRIES, PETSC_TRUE));
    PetscCall(PetscViewerBinaryOpen(PETSC_COMM_WORLD, file_name, FILE_MODE_READ, &viewer));
    PetscCall(MatLoad(*X, viewer));
    PetscFunctionReturn(0);
}

PetscErrorCode create_W(Mat *graph_mat, Mat *W) {
    const PetscReal *cache;
    PetscReal aux_data[N];
    PetscInt cols[N];
    PetscReal row_data_cache[N];
    PetscFunctionBeginUser;
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "Begin creating W! \n"));
    PetscCall(MatConvert(*graph_mat, MATSAME, MAT_INITIAL_MATRIX, W));
    PetscCall(read_aux_file(aux_data));

    for(int i = 0; i < N; i++) cols[i] = i;

    for(int i = 0; i < N; i++) {
        PetscInt row[1];
        row[0] = i;
        PetscReal weight = aux_data[i];
        PetscCall(MatGetRow(*graph_mat, i-local_row_size, NULL, NULL, &cache));
        
        for(int j = 0; j < N; j++) {
            if(weight == 0.0) {
                row_data_cache[j] = 0.0;
            } else {
                row_data_cache[j] = cache[j]/weight;
            }
        }

        PetscCall(MatSetValuesLocal(*W, 1, row, N, cols, row_data_cache, INSERT_VALUES));
        PetscCall(MatRestoreRow(*graph_mat, i-local_row_size, NULL, NULL, &cache));
        if(i%10 == 0) {
            MatAssemblyBegin(*W, MAT_FLUSH_ASSEMBLY);
            MatAssemblyEnd(*W, MAT_FLUSH_ASSEMBLY);
        }
        PetscCall(PetscPrintf(PETSC_COMM_WORLD, "%f - W - done! \n", (1.0*i)/(N)));
    }
    MatAssemblyBegin(*W, MAT_FINAL_ASSEMBLY);
    MatAssemblyEnd(*W, MAT_FINAL_ASSEMBLY);

    PetscCall(output_matrix(W, "W.mat"));
    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "End creating W! \n"));
    PetscFunctionReturn(0);
}

PetscErrorCode prepare_pagerank_W(Mat *W) {
    const PetscReal *cache;
    Mat pgr_W;
    PetscReal aux_data[N];
    PetscInt cols[N];
    PetscReal row_data_cache[N];
    PetscInt l_start, l_end;
    PetscReal col_sums[N];
    Vec col_sums_vec;
    PetscFunctionBeginUser;
    PetscCall(PetscPrintf(PETSC_COMM_SELF, "Begin creating PageRank matrix! \n"));
    PetscCall(MatTranspose(*W, MAT_INITIAL_MATRIX, &pgr_W));
    PetscCall(MatGetColumnSums(pgr_W, col_sums));
    PetscCall(VecCreateSeq(PETSC_COMM_SELF, N, &col_sums_vec));
    for(int i = 0; i < N; i++) PetscCall(VecSetValue(col_sums_vec, i, 1.0/((col_sums[i] == 0) ? 1.0 : col_sums[i]), INSERT_VALUES));
    PetscCall(VecAssemblyBegin(col_sums_vec));
    PetscCall(VecAssemblyEnd(col_sums_vec));

    PetscCall(PetscPrintf(PETSC_COMM_SELF, "Begin diagonal scale! \n"));
    PetscCall(MatDiagonalScale(pgr_W, NULL, col_sums_vec));

    PetscCall(output_matrix(&pgr_W, "pgr_W.mat"));
    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "End creating pgr_W! \n"));
    PetscFunctionReturn(0);
}

PetscErrorCode write_vec_view(Vec *vec, const char * file_name) {
    PetscViewer viewer;
    PetscFunctionBeginUser;
    PetscCall(PetscViewerCreate(PETSC_COMM_WORLD, &viewer));
    PetscCall(PetscViewerSetType(viewer, PETSCVIEWERASCII));
    PetscCall(PetscViewerSetFormat(viewer, PETSC_VIEWER_ASCII_MATLAB));
    PetscCall(PetscViewerFileSetMode(viewer, FILE_MODE_WRITE));
    PetscCall(PetscViewerFileSetName(viewer, file_name));
    PetscCall(VecView(*vec, viewer));
    PetscCall(PetscViewerDestroy(&viewer));
    PetscFunctionReturn(0);

    PetscFunctionReturn(0);
}

PetscErrorCode compute_pagerank(Mat *W_pgr) {
    Vec prev, curr_loc, res, curr;
    PetscRandom rctx;
    PetscReal step_norm;
    VecScatter sc_ctx;
    PetscFunctionBeginUser;
    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "Begin - Compute PageRank!\n"));
    PetscCall(PetscRandomCreate(PETSC_COMM_WORLD, &rctx));
    PetscCall(VecCreate(PETSC_COMM_SELF, &curr_loc));
    PetscCall(VecCreate(PETSC_COMM_WORLD, &curr));
    PetscCall(VecSetType(curr_loc, VECSTANDARD));
    PetscCall(VecSetType(curr, VECSTANDARD));
    PetscCall(VecSetSizes(curr_loc, N, N));
    PetscCall(VecSetSizes(curr, local_row_size, N));
    PetscCall(VecDuplicate(curr, &prev));
    PetscCall(VecSet(prev, 1.0));
    PetscCall(VecSetRandom(curr, rctx));

    PetscCall(VecScatterCreateToAll(curr, &sc_ctx, &curr_loc));

    do {
        VecScatterBegin(sc_ctx,curr,curr_loc, INSERT_VALUES, SCATTER_FORWARD);
        VecScatterEnd(sc_ctx,curr,curr_loc, INSERT_VALUES, SCATTER_FORWARD);
        PetscCall(MatMult(*W_pgr, curr_loc, curr));
        PetscCall(VecAXPY(prev, -1.0, curr));
        PetscCall(VecNorm(prev, NORM_2, &step_norm));
        PetscCall(VecCopy(curr, prev));
        PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD,"Norm2 diff: %f\n", step_norm));
    } while (step_norm > 0.05);

    write_vec_view(&curr, "PageRank.txt");
    PetscCall(PetscSynchronizedPrintf(PETSC_COMM_WORLD, "End - Compute PageRank!\n"));
    PetscFunctionReturn(0);
}

int main(int argc, char **args) {
    PetscInitialize(&argc, &args, (char *)0, "");
    MPI_Comm_size(PETSC_COMM_WORLD, &proc_size);
    MPI_Comm_rank(PETSC_COMM_WORLD, &self_rank);

    local_row_size = N/proc_size + ((self_rank < (N%proc_size)) ? 1 : 0);

    PetscBool file_graph_mat_exists;
    PetscBool file_W_exists;
    char file_graph_mat[128];
    char file_W[128];
    char file_W_pagerank[128];
    Mat graph_mat, W_pgr, W;
    PetscCall(PetscOptionsGetString(NULL, NULL, "-graph_mat", file_graph_mat, sizeof(file_graph_mat), NULL));
    PetscCall(PetscOptionsGetString(NULL, NULL, "-W", file_W, sizeof(file_W), NULL));
    PetscCall(PetscOptionsGetString(NULL, NULL, "-W_pagerank", file_W_pagerank, sizeof(file_W_pagerank), NULL));
    PetscCall(PetscTestFile(file_graph_mat, '\0', &file_graph_mat_exists));
    PetscCall(PetscTestFile(file_W, '\0', &file_W_exists));
    if(!file_graph_mat_exists || !file_W_exists) {
        if(main_thread_rank == self_rank) {
            // Initial computing faster on a single thread
            PetscCall(PetscPrintf(PETSC_COMM_SELF, "ENTERING!"));
            PetscCall(create_graph_mat(&graph_mat));
            PetscCall(create_W(&graph_mat, &W));
            PetscCall(MatDestroy(&graph_mat));
            PetscCall(prepare_pagerank_W(&W));
            PetscCall(MatDestroy(&W));
        }
        PetscCall(PetscBarrier(NULL));
    }

    // A lot faster to compute on many threads
    PetscCall(read_matrix(&W_pgr, file_W_pagerank));
    PetscCall(compute_pagerank(&W_pgr));

    PetscCall(PetscFinalize());
    return 0;
}