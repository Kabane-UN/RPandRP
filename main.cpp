#include <iostream>
#include <omp.h>

#include <vector>
#include <cmath>


using namespace std;

# define N pow(2, 12)
# define S (int)N

void gen_matrix(vector<vector<double>> &a, vector<double> &b){
    for (int i = 0; i < N; i++){
        vector<double> g;
        for (int j = 0; j < N; j++){
            if (i == j){
                g.push_back(2.0);
            } else {
                g.push_back(1.0);
            }
        }
        a.push_back(g);
        b.push_back(N + 1);
    }
}

vector<vector<vector<double>>> sep_by_lines(vector<vector<double>> a, int n){
    vector<vector<vector<double>>> as;
    int t = a.size() / n;
    int i = 0;
    while (i != a.size())
    {
        vector<vector<double>> g;
        for (int j = i; j < i + t; j++){
            g.push_back(a[j]);
        }
        as.push_back(g);
        i += t;
    }
    return as;
    
}

vector<vector<double>> sep_by_lines(vector<double> a, int n){
    vector<vector<double>> as;
    int t = a.size() / n;
    int i = 0;
    while (i != a.size())
    {
        vector<double> g;
        for (int j = i; j < i + t; j++){
            g.push_back(a[j]);
        }
        as.push_back(g);
        i += t;
    }
    return as;
    
}

vector<double> matrix_apply(vector<vector<double>> a, vector<double> x){
    vector<double> res;
    for (int i = 0; i < a.size(); i++){
        double s = 0;
        for (int j = 0; j < a[i].size(); j++){
            s += a[i][j] * x[j];
        }
        res.push_back(s);
    }
    return res;
}
vector<double> matrix_minus(vector<double> a, vector<double> b){
    vector<double> res;
    for (int i = 0; i < a.size(); i++){
        res.push_back(a[i] - b[i]);
    }
    return res;
}

double matrix_norm(vector<double> a){
    double res = 0;
    for (int i = 0; i < a.size(); i++){
        res += pow(a[i], 2);
    }
    return sqrt(res);
}

vector<double> matrix_sign_mul(double r, vector<double> a){
    vector<double> res;
    for (int i = 0; i < a.size(); i++){
        res.push_back(r * a[i]);
    }
    return res;
}

vector<double> f(vector<vector<double>> a, vector<double> b, vector<double> x, vector<double> xx, int n, bool neg){
    if (!neg){
        return matrix_minus(xx, matrix_sign_mul(0.1 / n, matrix_minus(matrix_apply(a, x), b)));
    } else {
        return matrix_minus(xx, matrix_sign_mul(- 0.1 / n, matrix_minus(matrix_apply(a, x), b)));
    }
}
double g(vector<vector<double>> a, vector<double> x, vector<double> b){
    return matrix_norm(matrix_minus(matrix_apply(a, x), b)) / matrix_norm(b);
}

int main(int argc, char** argv){
    vector<vector<double>> a;
    vector<double> b;
    gen_matrix(a, b);
    vector<vector<vector<double>>> as = sep_by_lines(a, S);
    vector<double> x(N);
    for (int i = 0; i < N; i++){
        x[i] = 0;
    }
    bool flag = true;
    bool neg = false;
    double e = g(a, x, b);
    while (flag) {
        vector<vector<double>> gg(S);
        vector<vector<double>> Bs = sep_by_lines(b, S);
        vector<vector<double>> Xs = sep_by_lines(x, S);
        # pragma omp parallel
        {
            # pragma omp for nowait
            for (int i = 0; i < S; i++) {
                
                vector<double> res = f(as[i], Bs[i], x, Xs[i], b.size(), neg);
                
                gg[i] = res;
            }
        }
        vector<double> nx;
        for (int i = 0; i < gg.size(); i++){
            for (int j = 0; j < gg[i].size(); j++){
                nx.push_back(gg[i][j]);
            }
        }
        x = nx;
        double ne = g(a, x, b);
        if (ne < 0.00001){
            flag = false;
        } else if (ne > e){
            neg = !neg;
        }
        e = ne;
    }
    
    return 0;
}